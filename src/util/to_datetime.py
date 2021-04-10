from datetime import datetime

# 監視ログの日時文字列をdatetime型に変換する
def to_datetime(string_datetime):
  return datetime(
    year=int(string_datetime[0:4]),
    month=int(string_datetime[4:6]),
    day=int(string_datetime[6:8]),
    hour=int(string_datetime[8:10]),
    minute=int(string_datetime[10:12]),
    second=int(string_datetime[12:14])
  )
