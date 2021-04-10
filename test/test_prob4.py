import sys
import glob
import unittest

sys.path.append('.')

from src.prob4 import serveillance

class TestProblem1(unittest.TestCase):
  def test_serveillance(self):
    # テストデータを格納したファイルのリストを取得する
    test_file_list = glob.glob('test/data/prob4-*.txt')

    for test_file_path in test_file_list:
      # ファイルからテストデータを読み込む
      with open(test_file_path, 'r') as f:
        log_list, expected, clash_threshold, busy_threshold, busy_length = f.read().split('\n\n')
      log_list = log_list.split('\n')
      expected = expected.split('\n')
      clash_threshold = int(clash_threshold)
      busy_threshold = int(busy_threshold)
      busy_length = int(busy_length)

      # ログファイルの監視を実行する
      result = serveillance(log_list, clash_threshold, busy_threshold, busy_length)

      # 実行結果が期待するものになっているか確認する
      if expected == ['no_clash']:
        self.assertEqual([], result)
      else:
        self.assertEqual(expected, result)

if __name__ == '__main__':
  unittest.main()