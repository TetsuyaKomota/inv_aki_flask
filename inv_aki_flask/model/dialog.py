from typing import Optional

MessageData = tuple[str, str]
QAData = tuple[MessageData, MessageData, int]


class DialogData:
    def __init__(
        self,
        player_name: str,
        system_name: str,
        dialog: Optional[list[QAData]] = None,
    ) -> None:
        self.player_name = player_name
        self.system_name = system_name
        if dialog:
            self.dialog = dialog
        else:
            self.dialog = []

    def add(self, msg: str, ans: str) -> None:
        player_msg = (self.player_name, msg)
        system_msg = (self.system_name, ans)
        count = len(self.dialog)
        self.dialog.append((player_msg, system_msg, count))

    def get_latest_system_response(self) -> Optional[str]:
        if len(self.dialog) == 0:
            return None
        latest_msg = self.dialog[-1]
        latest_system_msg = latest_msg[1]
        res = latest_system_msg[1]
        return " ".join(res.split("\n"))

    def to_args(self) -> tuple[str, str, list[QAData]]:
        return (self.player_name, self.system_name, self.dialog)

    def __iter__(self):
        return iter(self.dialog)

    def __len__(self):
        return len(self.dialog)
