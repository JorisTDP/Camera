#!python3.9
class Status():
    def __init__(self, status_dict):
        self.status_dict = status_dict

    def get(self, key: str):
        return self.status_dict[key]

    def set(self, key: str, val):
        self.status_dict[key] = val
    
    def __str__(self):
        return f"status: {str(self.status_dict)}"

    @classmethod
    def default_status(cls):
        status_dict = {'status_text': "Starting/Connecting to Camera", 'current_mode': 0,
         'x_angle': 0, 'z_angle': 0, 'distance': 0, 'x_offset': 0, 'z_offset': 0,
         'modes': {0: "Radar controlled", 1: "Manual movement"}}

        return cls(status_dict)

    @classmethod
    def disconnected_status(cls):
        status = cls.default_status()

        status['status_text'] = "Disconnected"

        return status


