import sys
import os

from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# Mapping between piece ID and chess piece name
id_map = dict({1:"Red Pawn", 
               2:"Red Advisor", 
               3:"Red Elephant", 
               4:"Red Horse", 
               5:"Red Cannon", 
               6:"Red Chariot", 
               7:"Red King",    
              -1:"Black Pawn",
              -2:"Black Advisor",
              -3:"Black Elephant",
              -4:"Black Horse",
              -5:"Black Cannon",
              -6:"Black Chariot",
              -7:"Black King",
               0:"  ",})

class ShowMessageThread(QThread):   # Used for synchronization delay during pop-up window to ensure execution sequence

    signal = pyqtSignal(str, str)    # Signal for transmitting messages

    def __init__(self, title, text):

        super(ShowMessageThread, self).__init__()
        self.title = title
        self.text = text

    def run(self):

        self.signal.emit(self.title, self.text)  # Transmit signals for text content

class GameGUI(QWidget):   # Custom window class

    start_x = 145   # Horizontal axis offset of the chessboard in the form
    start_y = 90   # Vertical axis offset of the chessboard in the form
    chess_x = 65    # Length of the chess piece along the horizontal axis
    chess_y = 65    # Length of the chess piece along the vertical axis
    chess = []  # Label list
    move_start_x = -1    # Mark the position of the chess piece before it moves, used to highlight the chess piece for the operation. A value of -1 indicates blocking the operation
    move_start_y = -1   # Using the chessboard coordinate system, x is for vertical and y is for horizontal
    move_end_x = -1    # Mark the position of the chess piece after movement
    move_end_y = -1
    select_x = -1   # Mark the selected chess piece position
    select_y = -1
    window_x = 900  # Length of the form along the horizontal axis
    window_y = 800  # Length of the form along the vertical axis
    count = 0   # Count the number of times a chessboard is drawn and used for controlling the maximum of two draws
    board_reverse = False   # Flip the chessboard perspective, mainly used for "black"
    victory = None # Sign of the end of Game

    def __init__(self, window_name = "Chinese Chess"):

        super().__init__()
        self.window_init(window_name)  # Initialize the form
        
    def window_init(self, window_name):  # Initialize the form

        self.resize(self.window_x, self.window_y)    # Set window size
        screen = QDesktopWidget().screenGeometry()  # Calculate display screen size
        size = self.geometry()  # Get window size
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))  # Center the window
        self.setWindowTitle(window_name)   # Set title
        palette = QPalette()    # Palette Object
        palette.setColor(QPalette.Background,QColor(35, 143, 130))   # Set palette colors
        self.setPalette(palette)
        self.setFixedSize(self.width(), self.height())  # Fix window size

    def set_move_mark(self,flag_x = 10,flag_y = 10,pos_x = 10,pos_y = 10,des_x = 10,des_y = 10):    # Set chess piece movement markers
        
        # 10 means remain unchanged, -1 means not draw
        if flag_x != 10:   self.select_x = flag_x
        if flag_y != 10:   self.select_y = flag_y
        if pos_x != 10:   self.move_start_x = pos_x
        if pos_y != 10:   self.move_start_y = pos_y
        if des_x != 10:   self.move_end_x = des_x
        if des_y != 10:   self.move_end_y = des_y
        self.draw_flag = True

    def paintEvent(self,event):

        # Draw the chessboard up to two times to prevent duplicate drawing and improve efficiency
        if self.count > 1: return
        self.count += 1

        # Draw on the canvas and then draw on the form to achieve dual cache drawing
        self.canvas = QPixmap(self.window_x, self.window_y)
        self.canvas.fill(QColor(35, 143, 130))

        # Set the painter
        painter = QPainter(self.canvas)
        pen = QPen(Qt.black,2,Qt.SolidLine)
        painter.setPen(pen)

        # Draw Gridlines of chessboard
        for i in range(10):
            self.board_draw_line(i, 0, i, 8, painter)   # Draw line

        for i in range(9):
            self.board_draw_line(0, i, 4, i, painter)   # Draw column lines with a blank line in the middle
            self.board_draw_line(5, i, 9, i, painter)

        self.board_draw_line(4, 0, 5, 0, painter)   # Fill in the blank lines on both sides
        self.board_draw_line(4, 8, 5, 8, painter)
 
        self.board_draw_line(0, 3, 2, 5, painter)   # Draw the diagonal line of the Nine Palaces above the chessboard
        self.board_draw_line(0, 5, 2, 3, painter)
 
        self.board_draw_line(7, 3, 9, 5, painter)   # Draw the diagonal line of the Nine Palaces below the chessboard
        self.board_draw_line(7, 5, 9, 3, painter)

        # Draw the "楚河汉界"
        painter.setFont(QFont("Timers" , 28, QFont.Bold))
        painter.drawText(self.start_x + 2 * self.chess_x, int(self.start_y + 5.2 * self.chess_y), "楚河         汉界")
        
        # Draw a chessboard position annotation
        mark_map = ["九", "八", "七", "六", "五", "四", "三", "二", "一"]

        for i in range(9):
            t = i
            up_y = int(self.start_y - self.chess_y / 2)   # Vertical coordinates marked above the chessboard
            down_y = int(self.start_y - self.chess_y / 2 + 10.6 * self.chess_y) # Vertical coordinates marked below the chessboard

            # Perform coordinate transformation if needed to flip the perspective
            if self.board_reverse:
                up_y, down_y = down_y, up_y
                t = 8 - i

            up_x = int(self.start_x + self.chess_x / 2 + t * self.chess_x) - 5    # Horizontal coordinates marked above the chessboard
            down_x = up_x   # Horizontal coordinates marked below the chessboard

            # Draw red and black position markers
            painter.setFont(QFont("Timers", 16, QFont.Bold))
            painter.drawText(up_x, up_y + 20, str(i + 1))
            painter.drawText(down_x - 5, down_y + 20, mark_map[i])

        # Draw selected chess piece markers or position markers before and after chess piece movement
        # Draw the moving chess pieces with a red border
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)
        if self.move_start_x != -1:
            x = self.move_start_y
            y = self.move_start_x
            if self.board_reverse: # Need to flip view
                x = 8 - x
                y = 9 - y
            painter.drawRect(self.start_x + self.chess_x * x, self.start_y + self.chess_y * y, self.chess_x, self.chess_y)

        if self.move_end_x != -1: # Need to flip view
            x = self.move_end_y
            y = self.move_end_x
            if self.board_reverse:
                x = 8 - x
                y = 9 - y
            painter.drawRect(self.start_x + self.chess_x * x, self.start_y + self.chess_y * y, self.chess_x, self.chess_y)

        # The selected chess piece is drawn with a blue border and
        # when there is selected chess piece, they are placed behind the red border that covers the moving position
        pen = QPen(Qt.blue, 2, Qt.SolidLine)
        painter.setPen(pen)
        if self.select_x != -1:   # Need to flip view
            x = self.select_y
            y = self.select_x
            if self.board_reverse:
                x = 8 - x
                y = 9 - y
            painter.drawRect(self.start_x + self.chess_x * x, self.start_y + self.chess_y * y, self.chess_x, self.chess_y)

        # Implementing double buffered drawing
        painter_2 = QPainter(self)
        painter_2.drawPixmap(0, 0, self.canvas)

    def board_draw_line(self, begin_x, begin_y, end_x, end_y, painter):  # Draw lines using a chessboard array as coordinate points

        painter.drawLine(int(self.start_x + self.chess_y / 2 + begin_y * self.chess_y),
                        int(self.start_y + self.chess_x / 2 + begin_x * self.chess_x),
                        int(self.start_x + self.chess_y / 2 + end_y * self.chess_y),
                        int(self.start_y + self.chess_x / 2 + end_x * self.chess_x))

    def changeEvent(self,event):    # When zooming the window, redraw the chessboard lines

        self.count = 0
        self.update()

    def resizeEvent(self,event):    # When resizing the window, redraw the chessboard lines
        
        self.count = 0
        self.update()

    def GameShow(self,board): # Redraw interface

        self.count = 0  # Redraw gridlines of chessboard
        self.update()

        for i in range(len(self.chess)):
            self.chess[i].deleteLater() # Clear all previous labels
        self.chess = [] # Clear label list
        
        for i in range(10):
            for j in range(9):
                if board[i][j] != 0:
                    name = id_map.get(board[i][j])  # Get the corresponding name of the chess piece
                    label = QLabel(self)    # New label

                    # Place chess pieces at corresponding positions on the interface
                    if(self.board_reverse):    # Flip the view if your side is black
                        label.move(self.start_x + (8 - j) * self.chess_x, self.start_y + (9 - i) * self.chess_y)
                    else:
                        label.move(self.start_x + j * self.chess_x, self.start_y + i * self.chess_y)

                    label.resize(self.chess_x, self.chess_y) # Set label size

                    # Get image location
                    path = os.path.dirname(os.path.abspath(__file__))   # Get relative path, omit qrc file
                    folder_name = "image"
                    file_name = f"{name}.png"
                    path = os.path.join(path, folder_name)
                    path = os.path.join(path, file_name)

                    label.setPixmap(QPixmap(path).scaled(self.chess_x, self.chess_y))    # Load images and set image size
                    label.show()    # Output label content and display chess pieces
                    self.chess.append(label)    # Add tags to the tag array for recording and refreshing the interface

    def show_MessageBox(self, title, text): # Pop up function at the end of the game

        QMessageBox.information(self, title, text)

if __name__ == "__main__":

    app = QApplication(sys.argv)    # Establish a QApplication object
    window = GameGUI()    # Create window object
    window.show()   # Display main window
    sys.exit(app.exec_())   # Main cycle

