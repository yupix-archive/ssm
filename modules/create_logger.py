import coloredlogs
from logging import getLogger, StreamHandler, DEBUG, Formatter, addLevelName

"""create easy logger"""


class EasyLogger:
	def __init__(self, logger=None):
		self.logger = logger

	def create(self):
		"""create logger"""
		# loggerのログレベル設定(ハンドラに渡すエラーメッセージのレベル)
		self.logger.setLevel(DEBUG)

		# --------------------------------
		# 2.handlerの設定
		# --------------------------------
		# handlerの生成
		stream_handler = StreamHandler()

		# handlerのログレベル設定(ハンドラが出力するエラーメッセージのレベル)
		stream_handler.setLevel(DEBUG)

		# --------------------------------
		# 3.loggerにhandlerをセット
		# --------------------------------
		self.logger.addHandler(stream_handler)
		self.logger.propagate = False

		coloredlogs.CAN_USE_BOLD_FONT = True
		coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'},
		                                    'hostname': {'color': 'magenta'},
		                                    'levelname': {'color': 'black', 'bold': True},
		                                    'name': {'color': 'blue'},
		                                    'programname': {'color': 'cyan'}
		                                    }
		coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'color': 'red', 'bold': True},
		                                    'error': {'color': 'red'},
		                                    'warning': {'color': 'yellow'},
		                                    'notice': {'color': 'magenta'},
		                                    'info': {'color': 'green'},
		                                    'debug': {},
		                                    'spam': {'color': 'green', 'faint': True},
		                                    'success': {'color': 'green', 'bold': True},
		                                    'verbose': {'color': 'blue'}
		                                    }

		coloredlogs.install(level='DEBUG', logger=self.logger, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

		# SUCCESSを追加
		self.logger.SUCCESS = 25  # WARNINGとINFOの間
		addLevelName(self.logger.SUCCESS, 'SUCCESS')
		setattr(self.logger, 'success', lambda message, *args: self.logger._log(self.logger.SUCCESS, message, args))
		return self.logger


if __name__ == "__main__":
	EasyLogger()
