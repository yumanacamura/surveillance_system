import sys
from datetime import datetime
from collections import deque

sys.path.append('src')

from prob2 import ServerState as oldServerState
from util.to_datetime import to_datetime

# サーバ1つの状態を格納するクラス
class ServerState(oldServerState):
  def __init__(self, server_address, clash_threshold=1, busy_threshold=100, busy_length=1):
    super().__init__(server_address)
    self.busy_threshold = busy_threshold
    self.busy_length = busy_length
    self.ping_list = deque([0]*busy_length)
    self.is_busy = False

  def update(self, ping_datetime, ping_response):
    # pingの時刻と応答からサーバの状態を更新する
    if ping_response != '-':
      # pingがタイムアウトしていない場合
      # 過負荷状態を監視するためのping値配列を更新する
      self.ping_list.popleft()
      self.ping_list.append(int(ping_response))

    if ping_response == '-' and self.is_working == True:
      # 動作状態にあるサーバからpingが返ってこない場合
      # サーバが故障したと判断して状態を更新する
      self.clash(ping_datetime)
      return None
    else:
      # サーバがタイムアウトしていない場合、タイムアウト回数をリセットする
      self.clash_count = 0

    if ping_response != '-' and self.is_working == False:
      # 故障状態にあるサーバからpingが返ってきた場合
      # サーバが復旧したと判断して状態を更新する
      # サーバの故障期間を出力する
      return self.recover(ping_datetime)

    if ((sum(self.ping_list) / self.busy_length) > self.busy_threshold) and self.is_busy == False:
      # 過負荷状態でないサーバのpingの平均応答時間が閾値を上回った場合
      # サーバが過負荷になったと判断して状態を更新する
      self.busy(ping_datetime)

    if ((sum(self.ping_list) / self.busy_length) <= self.busy_threshold) and self.is_busy == True:
      # 過負荷状態のサーバのpingの平均応答時間が閾値を下回った場合
      # 過負荷が解消された判断して状態を更新する
      # サーバの過負荷期間を出力する
      return self.not_busy(ping_datetime)

    # サーバの状態に変化がない
    return None

  def busy(self, ping_datetime):
    # サーバが過負荷になった時、過負荷フラグをTrueにして過負荷開始時刻を保存する
    self.busy_from = ping_datetime
    self.is_busy = True

  def not_busy(self, ping_datetime):
    # サーバが過負荷でなくなった時、過負荷フラグをFalseにして過負荷期間を出力する
    self.is_busy = False
    return 'server {address} was busy : from {busy_time} to {recover_time}'.format(
      address=self.server_address,
      busy_time=self.busy_from,
      recover_time=ping_datetime
    )

  def finish(self):
    # サーバの監視が終了する時、サーバが故障状態ならそれを出力する
    if self.is_working == False:
      return 'server {address} was clashed : from {clash_time} to now'.format(
        address=self.server_address,
        clash_time=self.clash_from
      )

    # サーバの監視が終了する時、サーバが過負荷状態ならそれを出力する
    if self.is_busy == True:
      return 'server {address} was busy : from {busy_time} to now'.format(
        address=self.server_address,
        busy_time=self.busy_from
      )

    # サーバが動作状態なら何も出力しない
    return None

# サーバの監視ログリストからサーバの故障を検知する
def serveillance(log_list, clash_threshold, busy_threshold, busy_length):
  # 監視対象のサーバアドレスをキーとしてサーバの状態を格納する辞書を作成
  server_state_dict = dict()

  # 監視ログを読み込んで故障を検知する
  serveillance_result = []
  for log_line in log_list:
    # ログの文字列を各情報に分割する
    ping_datetime, server_address, ping_response = log_line.split(',')

    # pingの日時をstrからdatetimeに変換する
    ping_datetime = to_datetime(ping_datetime)

    # サーバが監視対象の辞書にない場合、新しく追加する
    if server_address not in server_state_dict:
      server_state_dict[server_address] = ServerState(server_address, clash_threshold, busy_threshold, busy_length)
    
    # サーバの状態を更新する
    result = server_state_dict[server_address].update(ping_datetime, ping_response)

    # サーバの状態について出力がある場合、保存する
    if result != None:
      serveillance_result.append(result)

  # 各サーバの監視を終了する
  for server in server_state_dict.values():
    result = server.finish()
    # サーバの状態について出力がある場合、保存する
    if result != None:
      serveillance_result.append(result)
  
  return serveillance_result

if __name__ == '__main__':
  log_file_path = input('監視ログファイル : ')
  clash_threshold = int(input('故障と判定するまでのタイムアウト回数 : '))
  busy_threshold = int(input('サーバが過負荷と判定する平均応答時間(ms) : '))
  busy_length = int(input('平均応答時間を求める際にしようする応答数 : '))

  with open(log_file_path, 'r') as f:
    log_list = [line.rstrip() for line in f.readlines()]

  print('\n'.join(serveillance(log_list, clash_threshold, busy_threshold, busy_length)))