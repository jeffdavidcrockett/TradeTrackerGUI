import sys
import sqlite3
import datetime
import ctypes
from PyQt4 import QtGui, QtCore
from traderGUI import Ui_MainWindow

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt4.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt4.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class AddTradePopup(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(AddTradePopup, self).__init__(parent)
       	self.setWindowTitle(' ')
       	self.setWindowIcon(QtGui.QIcon('exclamation.png'))
       	self.setFixedSize(550, 300)
       	self.state = 'Hold'
       	self.label = QtGui.QLabel(self)
       	self.label.setText("Are you sure you'd like to "
       			              "\nlog this trade?")
       	self.label.move(100, 80)
       	self.label.resize(500, 70)

       	self.yes_btn = QtGui.QPushButton(self)
       	self.yes_btn.setText('Yes')
       	self.yes_btn.move(100, 200)
       	self.yes_btn.resize(150, 60)
       	self.yes_btn.clicked.connect(self.yes_clicked)

       	self.no_btn = QtGui.QPushButton(self)
       	self.no_btn.setText('No')
       	self.no_btn.move(300, 200)
       	self.no_btn.resize(150, 60)
       	self.no_btn.clicked.connect(self.no_clicked)

    def yes_clicked(self):
    	self.state = 'Add'

    def no_clicked(self):
    	self.state = False


class TradeApp(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.setWindowIcon(QtGui.QIcon("line.png"))
		self.setWindowTitle('Trade Tracker')

		self.add_popup = AddTradePopup()

		self.issue_labels = [self.poor_rr_display, 
							 self.entered_soon_display,
							 self.entered_late_display, 
							 self.exited_soon_display,
							 self.exited_late_display, 
							 self.unplanned_display,
							 self.stop_display, 
							 self.too_large_display,
							 self.hesitated_display
							 ]

		self.issue_labels_past = [self.poor_rr_display_2, 
								  self.entered_soon_display_2,
							      self.entered_late_display_2, 
							      self.exited_soon_display_2,
							      self.exited_late_display_2, 
							      self.unplanned_display_2,
							      self.stop_display_2, 
							      self.too_large_display_2,
							      self.hesitated_display_2
							      ]

		self.current_date = str(datetime.date.today())
		self.months_dict = {'01': 'January', '02': 'February', '03': 'March', '04': 'April',
				            '05': 'May', '06': 'June', '07': 'July', '08': 'August', 
				            '09': 'September', '10': 'October', '11': 'November', '12': 'December'}

		for month in self.months_dict:
			if month == self.current_date[5:7]:
				self.curr_month = self.months_dict[month]

		self.yearly_win_label.setText('Yearly Win Rate for: ' + self.current_date[:4])
		self.monthly_win_label.setText('Monthly Win Rate for: ' + self.curr_month)
		self.year_lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
		self.month_lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
		self.today_lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
		self.year_switch_btn.clicked.connect(self.curr_yearly_issues)
		self.month_switch_btn.clicked.connect(self.curr_monthly_issues)
		self.rr_btn.clicked.connect(self.calculate_rr)
		self.percent_move_btn.clicked.connect(self.calculate_move)
		self.datetime_display.setText(self.current_date)
		self.add_trade_btn.clicked.connect(self.add_trade_to_db)
		self.past_stats_search_btn.clicked.connect(self.get_past_stats)
		# SQL argument tuples
		self.year = (self.current_date[:4],)
		self.year_month = (self.current_date[:7].replace('-', ' '),)
		
		self.get_display_data()

	def calculate_rr(self):
		'''Calculates the risk:reward ratio based on values the user provides.'''
		entry_price = float(self.entry_input.text())
		target_price = float(self.target_input.text())
		stop_loss = float(self.stop_input.text())
		diff_1 = target_price - entry_price
		diff_2 = entry_price  - stop_loss

		try:
			reward = round(diff_1 / diff_2, 1)
			self.ratio_display.setText('1:'+ str(reward))
		except ZeroDivisionError:
			self.ratio_display.setText("1:0")

	def calculate_move(self):
		'''Calculates the percentage size of a price move.'''
		before_val = float(self.before_val_input.text())
		current_val = float(self.current_val_input.text())
		
		try:
			percentage = round((current_val-before_val)/before_val*100, 2)
			self.percent_move_display.setText(str(percentage) + '%')
		except ZeroDivisionError:
			self.percent_move_display.setText('')

	def get_win_rate(self, trade_count, win_count):
		'''Returns either the monthly or yearly win rate.'''
		try:
			return round((win_count / trade_count) * 100, 1)
		except ZeroDivisionError:
			return 0

	def get_display_data(self):
		'''Queries values from database:
					- Total# of trades today
					- Total# of trades this month
					- Total# of trades this year
					- Total# of wins this year
					- Total# of wins this month

			Displays info onto lcd displays, and calculates
			monthly and yearly win rate percentage values. Inputs
			into progress bars.'''
		num_of_trades_today = db.num_of_trades_today((self.current_date,))
		num_of_trades_month = db.num_of_trades_month(self.year_month)
		num_of_trades_year = db.num_of_trades_year(self.year)
		num_of_wins_year = db.num_of_wins_year(self.year)
		num_of_wins_month = db.num_of_wins_month(self.year_month)

		self.today_lcd.display(num_of_trades_today)
		self.month_lcd.display(num_of_trades_month)
		self.year_lcd.display(num_of_trades_year)

		yearly_win_percent = self.get_win_rate(num_of_trades_year, num_of_wins_year)
		monthly_win_percent = self.get_win_rate(num_of_trades_month, num_of_wins_month)
		
		self.year_bar.setValue(yearly_win_percent)
		self.month_bar.setValue(monthly_win_percent)
		self.year_percent_label.setText(str(yearly_win_percent) + '%')
		self.month_percent_label.setText(str(monthly_win_percent) + '%')

		self.curr_yearly_issues()

	def get_issues_data(self, issues, labels):
		formatted_list = []
		percentage_list = []
		
		for i in range(len(issues)):
			formatted_list.append(issues[i][0][0])
		
		total_issues = sum(formatted_list)

		for i in range(9):
			try:
				percentage = round((formatted_list[i] / total_issues) * 100)
				percentage_list.append(percentage)
			except ZeroDivisionError:
				percentage = 0
				percentage_list.append(percentage)

		for i in range(9):
			labels[i].setText(str(percentage_list[i]) +'%')

	def curr_monthly_issues(self):
		self.label_18.setText('Trading Issues for ' + self.curr_month)
		issues = db.num_of_each_issue_month(self.year_month)
		self.get_issues_data(issues, self.issue_labels)

	def curr_yearly_issues(self):
		self.label_18.setText('Trading Issues for ' + self.current_date[:4])
		issues = db.num_of_each_issue_year(self.year)
		self.get_issues_data(issues, self.issue_labels)

	def get_past_stats(self):
		year = self.past_year_entry.text()

		if len(year) == 4:
			if self.past_month_menu.currentIndex() == 0:
				self.label_4.setText('Trading Issues for ' + year)
				formatted_year = (year,)
				issues = db.num_of_each_issue_year(formatted_year)
				self.get_issues_data(issues, self.issue_labels_past)
			else:
				month = self.past_month_menu.currentText()
				for m in self.months_dict:
					if m == month:
						month_str = self.months_dict[m]

				self.label_4.setText('Trading issues for ' + month_str + ' ' + year)
				formatted_month_year = (year + ' ' + month,)
				issues = db.num_of_each_issue_month(formatted_month_year)
				self.get_issues_data(issues, self.issue_labels_past)
			
	def add_trade_to_db(self):
		'''Activates popup window to confirm user wants to log trade.
		   If user selects "Yes", trade is logged. Retrieves trade 
		   data from input fields and calls database method to log 
		   the trade. If "No" then popup window is closed and method 
		   is left.'''
		self.add_popup.show()

		while True:
			QtCore.QCoreApplication.processEvents()
			
			if self.add_popup.state == 'Add':
				self.add_popup.close()
				trade_issue = None
				if self.trade_outcome_box.currentIndex() == 0:
					trade_outcome = 'W'
				else:
					trade_outcome = 'L'
				if self.reason_box.currentIndex() != 0:
					trade_issue = self.reason_box.currentIndex()

				trade_data = (self.current_date, trade_outcome, trade_issue)
				db.add_trade(trade_data)
				self.get_display_data()
				
				break
			elif not self.add_popup.state:
				self.add_popup.close()
				
				break

		self.add_popup.state = 'Hold'
			

class AppDatabase:
	'''Dedicated database class for logging trade data'''
	def __init__(self, db_file):
		'''Attemps to connect to database with provided filename, creates a trades
		   table with 3 columns. Columns consist of trade_date, trade_outcome, 
		   and trade_issue. Error will be displayed if error occurs.'''
		try:
			self.db_file = db_file
			self.conn = sqlite3.connect(self.db_file)
			self.cur = self.conn.cursor()
			self.cur.execute("""CREATE TABLE IF NOT EXISTS trades (trade_date TEXT,
																   trade_outcome TEXT,
																   trade_issue INTEGER
																   )""")
		except sqlite3.Error as error:
			print('An error occured: ', error)

	def add_trade(self, data):
		'''Inserts trade data into table'''
		self.cur.execute("INSERT INTO trades VALUES (?,?,?)", data)
		self.conn.commit()

	def num_of_trades_today(self, date):
		'''Query to get the total number of trades for current day'''
		self.cur.execute("SELECT count(*) FROM trades WHERE trade_date=?", date)
		result = self.cur.fetchall()
		return result[0][0]

	def num_of_trades_month(self, date):
		'''Query to get the total number of trades for current month'''
		self.cur.execute("SELECT count(*) FROM trades WHERE strftime('%Y %m', trade_date)=?", date)
		result = self.cur.fetchall()
		return result[0][0]

	def num_of_trades_year(self, year):
		'''Query to get the total number of trades for current year'''
		self.cur.execute("SELECT count(*) FROM trades WHERE strftime('%Y', trade_date)=?", year)
		result = self.cur.fetchall()
		return result[0][0]

	def num_of_wins_month(self, date):
		'''Query to get the total winning trades for current month'''
		self.cur.execute("""SELECT count(*) FROM trades WHERE strftime('%Y %m', trade_date)=?
						 AND trade_outcome='W'""", date)
		result = self.cur.fetchall()
		return result[0][0]

	def num_of_wins_year(self, year):
		'''Query to get the total winning trades for current year'''
		self.cur.execute("""SELECT count(*) FROM trades WHERE strftime('%Y', trade_date)=?
							AND trade_outcome='W'""", year)
		result = self.cur.fetchall()
		return result[0][0]

	def num_of_each_issue_year(self, year):
		'''Queries to get the number of each individual trading issues for the selected year.'''
		result_list = []

		sql = ["""SELECT count(*) FROM trades WHERE trade_issue=1 
				  AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=2 
			      AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=3 
				  AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=4 
				  AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=5 
				  AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=6 
				  AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=7 
				  AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=8 
				  AND strftime('%Y', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=9 
						    AND strftime('%Y', trade_date)=?"""
			   ]

		for query in sql:
			self.cur.execute(query, year)
			result_list.append(self.cur.fetchall())

		return result_list

	def num_of_each_issue_month(self, year_month):
		'''Queries to get the number of each individual trading issues for the selected month.'''
		result_list = []

		sql = ["""SELECT count(*) FROM trades WHERE trade_issue=1
				  AND strftime('%Y %m', trade_date)=?""", 
			   """SELECT count(*) FROM trades WHERE trade_issue=2
				  AND strftime('%Y %m', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=3
				  AND strftime('%Y %m', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=4
				  AND strftime('%Y %m', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=5
				  AND strftime('%Y %m', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=6
				  AND strftime('%Y %m', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=7
				  AND strftime('%Y %m', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=8
			      AND strftime('%Y %m', trade_date)=?""",
			   """SELECT count(*) FROM trades WHERE trade_issue=9
				  AND strftime('%Y %m', trade_date)=?"""
			   ]

		for query in sql:
			self.cur.execute(query, year_month)
			result_list.append(self.cur.fetchall())

		return result_list


db = AppDatabase('trade_db.db')
app = QtGui.QApplication(sys.argv)
trade_app = TradeApp()
trade_app.show()
sys.exit(app.exec_())
db.cur.close()
db.conn.close()

