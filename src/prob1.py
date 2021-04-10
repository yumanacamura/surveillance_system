from datetime import datetime
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

    if ping_response != '-' and self.is_working == False:
      # 故障状態にあるサーバからpingが返ってきた場合
      # サーバが復旧したと判断して状態を更新する
      self.recover(ping_datetime)

  def clash(self, ping_datetime):
    # サーバが故障した時、動作フラグをFalseにして故障開始時刻を保存する
    self.is_working = False
    self.clash_from = ping_datetime
  
  def recover(self, ping_datetime):
    # サーバが復旧した時、動作フラグをTrueにして故障期間を出力する
    self.is_working = True
    print('server {address} was clashed : from {clash_time} to {recover_time}'.format(
      address=self.server_address,
      clash_time=self.clash_from,
      recover_time=ping_datetime
    ))
  
  def __del__(self):
    # サーバの監視が終了する時、サーバが故障状態ならそれを出力する
    if self.is_working == False:
      print('server {address} was clashed : from {clash_time} to now'.format(
        address=self.server_address,
        clash_time=self.clash_from
      ))

# サーバの監視ログリストからサーバの故障を検知する
def serveillance(log_list):
  # 監視対象のサーバアドレスをキーとしてサーバの状態を格納する辞書を作成
  server_state_dict = dict()

  # 監視ログを読み込んで故障を検知する
  for log_line in log_list:
    # ログの文字列を各情報に分割する
    ping_datetime, server_address, ping_response = log_line.split(',')

    # pingの日時をstrからdatetimeに変換する
    ping_datetime = to_datetime(ping_datetime)

    # サーバが監視対象の辞書にない場合、新しく追加する
    if server_address not in server_state_dict:
      server_state_dict[server_address] = ServerState(server_address)
    
    # サーバの状態を更新する
    server_state_dict[server_address].update(ping_datetime, ping_response)

