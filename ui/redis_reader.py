import json
import time
import threading
import redis as redis_module
from queue import Queue, Full

RESPONSE_TIMEOUT = 3.0  # seconds to wait for a Redis response


class RedisReader:
    def __init__(self, q_channel_name, r_channel_name, r, psubscriber):
        self.q_channel_name = q_channel_name
        self.r_channel_name = r_channel_name
        self.redis_host = r.connection_pool.connection_kwargs['host']
        self.redis_port = r.connection_pool.connection_kwargs['port']
        self.nodes = []
        self.publisher = r
        self.mldict = {}
        self.rddict = {}
        self.message_counter = 1
        self.message_counter_lock = threading.Lock()
        self.refresh_lock = threading.Lock()
        self._stop_refresh = threading.Event()
        self.logQueue = Queue(maxsize=50)
        self.logLock = threading.Lock()

    def _next_m_id(self):
        with self.message_counter_lock:
            m_id = f'ui_{self.message_counter:05d}'
            self.message_counter += 1
            return m_id

    # ------------------------------------------------------------------
    # Core: subscribe-first, then publish, then poll
    # ------------------------------------------------------------------

    def _request(self, payload, node_id=None):
        """
        Subscribe to the response channel FIRST, then publish the request,
        then poll for the matching response. Uses a dedicated short-lived
        connection per request so threads never share a subscriber.
        """
        temp_r = redis_module.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
        temp_sub = temp_r.pubsub()
        temp_sub.subscribe(self.r_channel_name)
        # flush the subscribe confirmation message before publishing
        temp_sub.get_message(timeout=0.2)

        self.publisher.publish(self.q_channel_name, json.dumps(payload))
        self.log_message(payload)

        m_id = payload['m_id']
        deadline = time.monotonic() + RESPONSE_TIMEOUT
        try:
            while time.monotonic() < deadline:
                msg = temp_sub.get_message(ignore_subscribe_messages=True, timeout=0.05)
                if msg is None:
                    continue
                if msg['type'] != 'message':
                    continue
                try:
                    data = json.loads(msg['data'])
                except (json.JSONDecodeError, TypeError):
                    continue
                self.log_message(data)
                if data.get('responding_to') != m_id:
                    continue
                if node_id is not None and data.get('node_id') != node_id:
                    continue
                return data
        finally:
            temp_sub.unsubscribe()
            temp_r.close()
        return None



    def request_node_ids(self):
        request = {'m_type': 'get-nodes', 'm_id': self._next_m_id()}
        data = self._request(request)
        if data is None:
            print("Timeout waiting for node IDs")
            return []
        return data.get('nodes', [])

    def request_raw_node_data(self, node_id):
        request = {'m_type': 'get-recent-raw-data', 'm_id': self._next_m_id(), 'node_id': node_id}
        data = self._request(request, node_id=node_id)
        if data is None:
            print(f"Timeout waiting for raw data for node {node_id}")
        return data

    def request_inference_output(self, node_id):
        request = {'m_type': 'get-recent-inference', 'm_id': self._next_m_id(), 'node_id': node_id}
        data = self._request(request, node_id=node_id)
        if data is None:
            print(f"Timeout waiting for inference output for node {node_id}")
        return data

    def updateNode(self, node_id, anomaly_value, user, timestamp):
        #old request
        # request = {
        #     'm_type': 'update-node',
        #     'm_id': self._next_m_id(),
        #     'node_id': node_id,
        #     'anomaly_value': anomaly_value,
        #     'user': user,
        # }
        request ={
            "m_type": "user-anomaly-feedback",
            "m_id": self._next_m_id(),
            "node_id": node_id,
            "timestamp": timestamp,
            "acknowledged_by": user,
            "user_feedback": "DISPUTE" #always Dispute assuming we only make the change if something is wrong.
        }
        self.publisher.publish(self.q_channel_name, json.dumps(request))
        self.log_message(request)



    def refresh(self, instant=False):
        if not instant:
            if self._stop_refresh.wait(timeout=10):
                return  # stop event set

        if self.publisher is None:
            raise RuntimeError("Publisher must be connected before refreshing")

        newmldict = {}
        newrddict = {}

        self.nodes = self.request_node_ids()
        if self.nodes:
            for node in self.nodes:
                raw = self.request_raw_node_data(node)
                if raw is not None:
                    newrddict[node] = raw

                inf = self.request_inference_output(node)
                if inf is not None:
                    newmldict[node] = inf

        with self.refresh_lock:
            self.rddict = newrddict
            self.mldict = newmldict

    def run(self):
        """Background refresh loop."""
        while not self._stop_refresh.is_set():
            print("Refreshing data from Redis...")
            self.refresh()
        print("Refresh thread stopping...")


    def getDicts(self):
        with self.refresh_lock:
            return dict(self.rddict), dict(self.mldict)

    def stop(self):
        self._stop_refresh.set()


    def log_message(self, message):
        with self.logLock:
            try:
                self.logQueue.put_nowait(message)
            except Full:
                self.logQueue.get_nowait()
                self.logQueue.put_nowait(message)

    def drain_log_queue(self):
        logs = []
        with self.logLock:
            while not self.logQueue.empty():
                logs.append(self.logQueue.get_nowait())
        return logs


    def test_publish(self):
        message = {
            'm_type': 'get-recent-inference',
            'm_id': 'ui_00006',
            'node_id': 'node_001',
        }
        self.publisher.publish(self.q_channel_name, json.dumps(message))