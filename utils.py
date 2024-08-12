from CallMetadata import CallMetadata


def log(message, call_info: CallMetadata | None = None):
    if call_info:
        print(f"[{call_info.get_current_duration():.2f} s]: {message}")
    else:
        print(f"[---]: {message}")
