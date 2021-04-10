import sys
from datetime import datetime
from collections import deque
import ipaddress

sys.path.append('src')

from prob3 import ServerState
from util.to_datetime import to_datetime

# サブネット1つの状態を格納するクラス
class SubnetState:
  def __init__(self, subnet_address):
    self.subnet_address = subnet_address
    self.server_list = []
    self.is_working = True
  

  def update(self, ping_datetime):
    # サブネットの状態を更新する
    # サブネット内のサーバ全てが故障している場合、サブネットが故障していると判断する
    is_working = False
    for server in self.server_list:
      is_working = is_working or server.is_working
    
    if is_working == False and self.is_working == True:
      # 動作状態にあるサブネットが故障した場合、状態を更新する
      self.clash(ping_datetime)
      return None

    if is_working == True and self.is_working == False:
      # 故障状態にあるサブネットが動作した場合
      # サブネットが復旧したと判断して状態を更新し故障期間を出力する
      return self.recover(ping_datetime)

    # サブネットの状態に変化がない
    return None

  def clash(self, ping_datetime):
    # サブネットが故障した時、動作フラグをFalseにして故障開始時刻を保存する
    self.is_working = False
    self.clash_from = ping_datetime
  
  def recover(self, ping_datetime):
    # サブネットが復旧した時、動作フラグをTrueにして故障期間を出力する
    self.is_working = True
    return 'subnet {subnet} was clashed : from {clash_time} to {recover_time}'.format(
      subnet=self.subnet_address,
      clash_time=self.clash_from,
      recover_time=ping_datetime
    )

  def finish(self):
    # サブネットの監視が終了する時、サブネットが故障状態ならそれを出力する
    if self.is_working == False:
      return 'subnet {subnet} was clashed : from {clash_time} to now'.format(
        subnet=self.subnet_address,
        clash_time=self.clash_from,
      )

    # サーバが動作状態なら何も出力しない
    return None


# サーバの監視ログリストからサーバの故障を検知する
def serveillance(log_list, clash_threshold, busy_threshold, busy_length):
  # 監視対象のサーバアドレスをキーとしてサーバの状態を格納する辞書を作成
  server_state_dict = dict()
  # サブネットのアドレスをキーとしてサブネットの状態を格納する辞書を作成
  subnet_state_dict = dict()

  # 監視ログを読み込んで故障を検知する
  serveillance_result = []
  for log_line in log_list:
    # ログの文字列を各情報に分割する
    ping_datetime, server_address, ping_response = log_line.split(',')

    # pingの日時をstrからdatetimeに変換する
    ping_datetime = to_datetime(ping_datetime)

    # サーバアドレスからサブネットのアドレスを取得する
    subnet_address = str(ipaddress.ip_interface(server_address).network)

    # サブネットが監視対象の辞書にない場合、新しく追加する
    if subnet_address not in subnet_state_dict:
      subnet_state_dict[subnet_address] = SubnetState(subnet_address)

    # サーバが監視対象の辞書にない場合、新しく追加する
    if server_address not in server_state_dict:
      server_state_dict[server_address] = ServerState(server_address, clash_threshold, busy_threshold, busy_length)
      subnet_state_dict[subnet_address].server_list.append(server_state_dict[server_address])
    
    # サーバの状態を更新する
    result = server_state_dict[server_address].update(ping_datetime, ping_response)

    # サーバの状態について出力がある場合、保存する
    if result != None:
      serveillance_result.append(result)

    # サブネットの状態を更新する
    result = subnet_state_dict[subnet_address].update(ping_datetime)

    # サブネットの状態について出力がある場合、保存する
    if result != None:
      serveillance_result.append(result)

  # 各サーバの監視を終了する
  for server in server_state_dict.values():
    result = server.finish()
    # サーバの状態について出力がある場合、保存する
    if result != None:
      serveillance_result.append(result)
  
  # 各サーバの監視を終了する
  for subnet in subnet_state_dict.values():
    result = subnet.finish()
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