import time


class CallMetadata:
    def __init__(self, call_id, caller):
        self.call_id = call_id
        self.caller = caller
        self.start_date = time.time()

        self.context_analytical = None
        self.chat_analytical = None

        self.context_results = None
        self.chat_results = None

        self.analysis_threads = []
        self.last_analysis_info = None
        self.last_analysis_length = None

    def get_current_duration(self):
        return time.time() - self.start_date

    def add_analysis(self, analysis_thread):
        self.analysis_threads.append(analysis_thread)

    def reset_analysis(self):
        self.analysis_threads = []
        self.last_analysis_info = None
        self.last_analysis_length = None
