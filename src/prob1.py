import sys
from datetime import datetime

sys.path.append('src')

from util.to_datetime import to_datetime

# サーバ1つの状態を格納するクラス
class ServerState:
  def __init__(self, server_address):
    self.is_working = True
    self.server_address = server_address
  
  def update(self, ping_datetime, ping_response):
    # pingの時刻と応答からサーバの状態を更新する
    if ping_response == '-' and self.is_working == True:
      # 動作状態にあるサーバからpingが返ってこない場合
      # サーバが故障したと判断して状態を更新する
      self.clash(ping_datetime)
      return None

    if ping_response != '-' and self.is_working == False:
      # 故障状態にあるサーバからpingが返ってきた場合
      # サーバが復旧したと判断して状態を更新する
      # サーバの故障期間を出力する
      return self.recover(ping_datetime)

    # サーバの状態に変化がない
    return None

  def clash(self, ping_datetime):
    # サーバが故障した時、動作フラグをFalseにして故障開始時刻を保存する
    self.is_working = False
    self.clash_from = ping_datetime
  
  def recover(self, ping_datetime):
    # サーバが復旧した時、動作フラグをTrueにして故障期間を出力する
    self.is_working = True
    return 'server {address} was clashed : from {clash_time} to {recover_time}'.format(
      address=self.server_address,
      clash_time=self.clash_from,
      recover_time=ping_datetime
    )
  
  def finish(self):
    # サーバの監視が終了する時、サーバが故障状態ならそれを出力する
    if self.is_working == False:
      return 'server {address} was clashed : from {clash_time} to now'.format(
        address=self.server_address,
        clash_time=self.clash_from
      )

    # サーバが動作状態なら何も出力しない
    return None

# サーバの監視ログリストからサーバの故障を検知する
def serveillance(log_list):
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
      server_state_dict[server_address] = ServerState(server_address)
    
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

  with open(log_file_path, 'r') as f:
    log_list = [line.rstrip() for line in f.readlines()]

  print('\n'.join(serveillance(log_list)))