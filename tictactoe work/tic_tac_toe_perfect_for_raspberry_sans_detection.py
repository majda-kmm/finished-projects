from typing import Optional, Tuple
import random as rand
import tkinter as tk
import definitions.boardclasses as bd
import definitions.tk_init as ini
import definitions.tk_util as ut
from PIL import Image, ImageTk
import os
from pygame import mixer
import sys
import communication.communication as com 
import ai.alphabetaV2 as al
import ai.alphabetaV5 as alV5
import mediapipe as mp
import cv2
from hand_tracking.module import findnameoflandmark, findpostion
from collections import Counter
from pynput.mouse import Controller, Button
import threading
"""Game Setup Constants"""

# OPPONENT SETTINGS
TWO_PLAYERS = "2 Players"
ONLINE = "Online"
VS_AI = "VS AI"
EASY = "Easy"
MEDIUM = "Medium"
HARD = "Hard"

# TURN ORDER (maybe not necessary for the game)
RANDOM_ORDER = "Random"
PLAYER_FIRST = "First"
PLAYER_SECOND = "Second"

"""Tkinter Initialization"""
root = tk.Tk()
root.geometry(f'{1400}x{800}')
root.title("GEMSTONE GRID")

# BACKGROUND IMAGE
welcome_img = Image.open("backgrounds/welcome.png")
photo_welcome = ImageTk.PhotoImage(welcome_img)
welcome_frame = tk.Frame(root)
welcome_frame.pack(fill=tk.BOTH, expand=True)
welcome_background = tk.Label(welcome_frame, image=photo_welcome)
welcome_background.place(x=0, y=0, relwidth=1, relheight=1)

GLOBALS = bd.GlobalVariables()
var = tk.IntVar()

def hand_tracking():
    mouse = Controller()

    # Initialize MediaPipe hand module and drawing utilities
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    # Initialize video capture from the webcam with reduced resolution and frame rate
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 15)

    tip_ids = [8, 12, 16, 20]

    selected = False

    toggle_detection_mode = 0

    lb_choice = False

    frame_skip = 3
    frame_count = 0


    # Configure MediaPipe hand detection
    with mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.9, min_tracking_confidence=0.9, max_num_hands=1) as hands:
        
        while True:
            ret, frame = cap.read()
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if GLOBALS.lb_state[str(GLOBALS.prev_local_col) + str(GLOBALS.prev_local_row)] == 1:
                lb_choice = True
            else:
                lb_choice = False
            

            # Skip frames to reduce processing
            if frame_count % frame_skip == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                # Get the hand landmarks and hand labels
                landmarks = findpostion(frame)
                landmark_names = findnameoflandmark(frame)

                # Check if landmarks are detected
                if landmarks and landmark_names:
                    finger_status = []

                    # Thumb check
                    if landmarks[0][1] < landmarks[4][1]:
                        finger_status.append(1)
                    else:
                        finger_status.append(0)

                    # Other fingers check
                    for id in tip_ids:
                        if landmarks[id][2] < landmarks[id - 2][2]:
                            finger_status.append(1)
                        else:
                            finger_status.append(0)

                    # Count the number of fingers up and down
                    finger_counter = Counter(finger_status)
                    up = finger_counter[1]
                    down = finger_counter[0]

                    if down == 4:
                        if GLOBALS.lb_for_hand == None:  
                            mouse.click(Button.left, 1)
                            selected = True
                        elif GLOBALS.mode_tracking == 2:
                            lb_choice = False
                            GLOBALS.prev_local_col = 3
                            GLOBALS.prev_local_row = 3
                            print('board selected')
                            cv2.waitKey(500)
                            
                        else:
                            root.event_generate("<<cell_selected>>")
                            cv2.waitKey(400)
                    elif down == 2:
                        if toggle_detection_mode == 1:
                            toggle_detection_mode = 0
                            cv2.waitKey(600)
                        else:
                            toggle_detection_mode = 1
                    else:
                        selected = False

                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    #mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS


                    for point in mp_hands.HandLandmark:
                        normalized_landmark = hand_landmarks.landmark[point]
                        pixel_coordinates = mp_drawing._normalized_to_pixel_coordinates(normalized_landmark.x, normalized_landmark.y,frame.shape[1], frame.shape[0])

                        if point == mp_hands.HandLandmark.MIDDLE_FINGER_MCP:
                            if pixel_coordinates:
                                x_coor, y_coor = pixel_coordinates

                                if GLOBALS.lb_for_hand == None or toggle_detection_mode == 1:
                                    GLOBALS.mode_tracking = 0
                                    mouse.position = ((-x_coor+320)*6, y_coor*4.5)

                                elif lb_choice == True:
                                    GLOBALS.mode_tracking = 2
                                    if x_coor < 106 and y_coor < 80:
                                    #if x_coor < 213 and y_coor < 160:
                                        j = 2
                                        print('Grille sélectionnée: ', 2)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[2]
                                        lb_choice == False
                                    if x_coor < 106 and 81 < y_coor < 160:
                                    #if x_coor < 213 and 161 < y_coor < 320:
                                        j = 5
                                        print('Grille sélectionnée: ', 5)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[5]
                                        lb_choice == False
                                    if x_coor < 106 and 161 < y_coor < 240:
                                    #if x_coor < 213 and 321 < y_coor < 480:
                                        j = 8
                                        print('Grillesélectionnée: ', 8)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[8]
                                        lb_choice == False

                                    if 106 < x_coor < 213 and y_coor < 80: 
                                    #if 214 < x_coor < 426 and y_coor < 160:
                                        j = 1
                                        print('Grille sélectionnée: ', 1)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[1]
                                        lb_choice == False
                                    if 106 < x_coor < 213 and 80 < y_coor < 160:
                                    #if 214 < x_coor < 426 and 161 < y_coor < 320:
                                        j = 4
                                        print('Grille sélectionnée: ', 4)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[4]
                                        lb_choice == False
                                    if 106 < x_coor < 213 and 160 < y_coor < 240:
                                    #if 214 < x_coor < 426 and 321 < y_coor < 480:
                                        j = 7
                                        print('Grille sélectionnée: ', 7)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[7]
                                        lb_choice == False
                                    
                                    if 213 < x_coor < 320 and y_coor < 80:
                                    #if 427 < x_coor < 640 and y_coor < 160:
                                        j = 0
                                        print('Grille sélectionnée: ', 0)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[0]
                                        lb_choice == False
                                    if 213 < x_coor < 320 and 80 < y_coor < 160:
                                    #if 427 < x_coor < 640 and 161 < y_coor < 320:
                                        j = 3
                                        print('Grille sélectionnée: ', 3)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[3]
                                        lb_choice == False
                                    if 213 < x_coor < 320 and 160 < y_coor < 240:
                                    #if 427 < x_coor < 640 and 321 < y_coor < 480:
                                        j = 6
                                        print('Grille sélectionnée: ', 6)
                                        GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[6]
                                        lb_choice == False
                                    for m in range(9) : 
                                        if j == m :
                                            perm_color = list_color[j]
                                            print(perm_color)
                                            ini.change_color(l[j],root,perm_color)

                                else:
                                    GLOBALS.mode_tracking = 1
                                    #if x_coor < 213 and y_coor < 160:
                                    if x_coor < 106 and y_coor < 80:
                                        i = 2

                                        GLOBALS.local_col = 2
                                        GLOBALS.local_row = 0
                                    #if x_coor < 213 and 161 < y_coor < 320:
                                    if x_coor < 106 and 81 < y_coor < 160:

                                        i = 5
                                        GLOBALS.local_col = 2
                                        GLOBALS.local_row = 1
                                    #if x_coor < 213 and 321 < y_coor < 480:
                                    if x_coor < 106 and 161 < y_coor < 240:
                                        i = 8

                                        GLOBALS.local_col = 2
                                        GLOBALS.local_row = 2
                                   
                                    #if 214 < x_coor < 426 and y_coor < 160:
                                    if 106 < x_coor < 213 and y_coor < 80:

                                        i = 1
                                        GLOBALS.local_col = 1
                                        GLOBALS.local_row = 0
                                    #if 214 < x_coor < 426 and 161 < y_coor < 320:
                                    if 106 < x_coor < 213 and 80 < y_coor < 160:
                                        i = 4
 
                                        GLOBALS.local_col = 1
                                        GLOBALS.local_row = 1
                                    #if 214 < x_coor < 426 and 321 < y_coor < 480:
                                    if 106 < x_coor < 213 and 160 < y_coor < 240:
                                   
                                        i = 7
                                        GLOBALS.local_col = 1
                                        GLOBALS.local_row = 2 
                                    
                                    #if 427 < x_coor < 640 and y_coor < 160:
                                    if 213 < x_coor < 320 and y_coor < 80:
                                        i = 0
                                  
                                        GLOBALS.local_col = 0
                                        GLOBALS.local_row = 0
                                    #if 427 < x_coor < 640 and 161 < y_coor < 320:
                                    if 213 < x_coor < 320 and 80 < y_coor < 160:
                                        i = 3
                            
                                        GLOBALS.local_col = 0
                                        GLOBALS.local_row = 1
                                    #if 427 < x_coor < 640 and 321 < y_coor < 480:
                                    if 213 < x_coor < 320 and 160 < y_coor < 240:
                                        i = 6
                                  
                                        GLOBALS.local_col = 0
                                        GLOBALS.local_row = 2
                                    for m in range(9) : 
                                        if i == m :
                                            ini.draw_and_erase_diamond(l[GLOBALS.lb_for_hand.index],root,GLOBALS.local_row,GLOBALS.local_col)

                                    


            frame_count += 1

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Release the capture and destroy all windows
    cap.release()
    cv2.destroyAllWindows()


def main_frame_packing():
    if 'online_window' in globals() :
        online_window.destroy()
    if 'offline_window' in globals():
        offline_window.destroy()
    if 'VS_AI_window' in globals():
        VS_AI_window.destroy()
    main_frame.pack(fill=tk.BOTH, expand=True)

def QUIT(window):
    global welcome_frame, offline_img
    welcome_frame = tk.Frame(root)
    window.pack_forget()
    window.destroy()

    offline_img = Image.open('offline.png')
    offline_img = offline_img.resize((230,70))
    offline_img = ImageTk.PhotoImage(offline_img)
    offline_button = tk.Button(root,command=play_offline,bd=0, highlightthickness=0)
    offline_button.config(image=offline_img)
    offline_button.place(relx=0.35, rely=0.47, anchor=tk.CENTER)

    online_img = Image.open('online.png')
    online_img = online_img.resize((230,70))
    online_img = ImageTk.PhotoImage(online_img)
    online_button = tk.Button(root,command=play_online,bd=0, highlightthickness=0)
    online_button.config(image=online_img)
    online_button.place(relx=0.8, rely=0.47, anchor=tk.CENTER)

def quit_program():
    """Quit the program and restart."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

def quit_parameters(window):
    window.destroy()

def parameter(window):

    global parameter_window, photo_parameter, rules_img, param_quit_img, credit_img, return_welcome_img
    global rules_text,credits_text, rules_visible, credits_visible
    rules_visible = False
    credits_visible = False

    parameter_window = tk.Toplevel(window)
    parameter_window.title("Parameter Window")
    parameter_window.geometry(f'{1400}x{900}')
    parameterwindow_img = Image.open("backgrounds/param_page.png")
    photo_parameter = ImageTk.PhotoImage(parameterwindow_img)
    parameter_background = tk.Label(parameter_window, image=photo_parameter)
    parameter_background.image = photo_parameter
    parameter_background.pack(fill=tk.BOTH, expand=True)

    rules_text = tk.Text(parameter_window, wrap=tk.WORD, state="disabled", bg="#82B5CB", fg="#000000",font='helvetica')

    credits_text = tk.Text(parameter_window, wrap=tk.WORD, state="disabled", bg="#82B5CB", fg="#000000",font='helvetica')

    rules_img = Image.open('buttons_img/rules.png')
    rules_img = rules_img.resize((175,47))
    rules_img = ImageTk.PhotoImage(rules_img)
    rules_button = tk.Button(parameter_window,command=toggle_rules,bd=0, highlightthickness=0)
    rules_button.config(image=rules_img)
    rules_button.place(relx=0.52, rely=0.36, anchor=tk.CENTER)

    credit_img = Image.open('buttons_img/credits.png')
    credit_img = credit_img.resize((175,47))
    credit_img = ImageTk.PhotoImage(credit_img)
    credit_button = tk.Button(parameter_window,command=toggle_credit,bd=0, highlightthickness=0)
    credit_button.config(image=credit_img)
    credit_button.place(relx=0.52, rely=0.527, anchor=tk.CENTER)

    param_quit_img = Image.open('buttons_img/close.png')
    param_quit_img = param_quit_img.resize((175,47))
    param_quit_img = ImageTk.PhotoImage(param_quit_img)
    param_quit_button = tk.Button(parameter_window,command=lambda : quit_parameters(parameter_window),bd=0, highlightthickness=0)
    param_quit_button.config(image=param_quit_img)
    param_quit_button.place(relx=0.87, rely=0.82, anchor=tk.CENTER)

    return_welcome_img = Image.open('buttons_img/quit.png')
    return_welcome_img = return_welcome_img.resize((165,42))
    return_welcome_img = ImageTk.PhotoImage(return_welcome_img)
    return_welcome_button = tk.Button(parameter_window,command=quit_program,bd=0, highlightthickness=0)
    return_welcome_button.config(image=return_welcome_img)
    return_welcome_button.place(relx=0.52, rely=0.68, anchor=tk.CENTER)

def toggle_rules():
    global rules_visible,rules_text, credits_visible, credits_text
    if credits_visible:
        credits_text.place_forget()
        credits_visible = False

    if rules_visible:
        rules_text.place_forget()
        rules_visible = False
    else:
        rules_text.config(state=tk.NORMAL)
        rules_text.delete('1.0', tk.END)  # Clear the text area before inserting new content
        try:
            with open('texts/rules.txt', 'r') as file:
                rules = file.read()
            rules_text.insert(tk.END, rules)  # Insert rules into the correct text widget
        except FileNotFoundError:
            rules_text.insert(tk.END, "Rules file not found.")  # Handle file not found error

        rules_text.config(state=tk.DISABLED)
        rules_text.place(relx=0.02, rely=0.3, anchor=tk.NW, width=590, height=370)
        rules_visible = True            

def toggle_credit():
    global rules_visible,rules_text, credits_visible, credits_text
    if rules_visible:
        rules_text.place_forget()
        rules_visible = False

    if credits_visible:
        credits_text.place_forget()
        credits_visible = False
    else:
        credits_text.config(state=tk.NORMAL)
        rules_text.delete('1.0', tk.END)  # Clear the text area before inserting new content
        try:
            with open('texts/credits.txt', 'r') as file:
                credits = file.read()
            credits_text.insert(tk.END, credits)  # Insert rules into the correct text widget
        except FileNotFoundError:
            credits_text.insert(tk.END, "Rules file not found.")  # Handle file not found error

        credits_text.config(state=tk.DISABLED)
        credits_text.place(relx=0.06, rely=0.3, anchor=tk.NW, width=290, height=200)
        credits_visible = True 

def play_offline():

    def play_VSHUMAN():
        GLOBALS.gamemode = TWO_PLAYERS

        main_frame_packing()
        draw_board()
        root.update()
        game_loop()

    def change_mode(difficulty):
        global line_to_write
        line_to_write = str(difficulty) + "AI"
        GLOBALS.bot_difficulty = str(difficulty)

    
    def change_turn(turn):
        if turn == "First":
            GLOBALS.player=1

        elif turn == "Second":
            GLOBALS.player=2

        else:
            GLOBALS.player = rand.randint(1,2)
        GLOBALS.bot = (GLOBALS.player%2)+1

    def start_game():
        main_frame_packing()
        draw_board()
        root.update()
        game_loop()
        
    def play_VSAI():
        GLOBALS.gamemode = VS_AI


        global VS_AI_window , photo_VSAI, EASY_img, medium_img, hard_img, you_img, ai_img, random_img, VSAIQUIT_img, paramvsai_img, play_img
        VS_AI_window = tk.Frame(root)
        offline_window.pack_forget()
        offline_window.destroy()
        VS_AI_window.pack(fill=tk.BOTH, expand=True)
        VSai_img = Image.open("backgrounds/menu_ai.png")
        photo_VSAI = ImageTk.PhotoImage(VSai_img)
        VSAI_background = tk.Label(VS_AI_window, image=photo_VSAI)
        VSAI_background.place(x=0, y=0, relwidth=1, relheight=1)


        # Create buttons for difficulty and turn
        EASY_img = Image.open('buttons_img/easy.png')
        EASY_img = EASY_img.resize((160,60))
        EASY_img = ImageTk.PhotoImage(EASY_img)
        EASY_button = tk.Button(VS_AI_window,command=lambda : change_mode("Easy"),bd=0, highlightthickness=0)
        EASY_button.config(image=EASY_img)
        EASY_button.place(relx=0.26, rely=0.33, anchor=tk.CENTER)

        medium_img = Image.open('buttons_img/medium.png')
        medium_img = medium_img.resize((160,60))
        medium_img = ImageTk.PhotoImage(medium_img)
        medium_button = tk.Button(VS_AI_window,command=lambda : change_mode("Medium"),bd=0, highlightthickness=0)
        medium_button.config(image=medium_img)
        medium_button.place(relx=0.52, rely=0.33, anchor=tk.CENTER)

        hard_img = Image.open('buttons_img/hard.png')
        hard_img = hard_img.resize((160,60))
        hard_img = ImageTk.PhotoImage(hard_img)
        hard_button = tk.Button(VS_AI_window,command=lambda : change_mode("Hard"),bd=0, highlightthickness=0)
        hard_button.config(image=hard_img)
        hard_button.place(relx=0.781, rely=0.33, anchor=tk.CENTER)

        you_img = Image.open('buttons_img/you.png')
        you_img = you_img.resize((160,60))
        you_img = ImageTk.PhotoImage(you_img)
        you_button = tk.Button(VS_AI_window,command=lambda : change_turn("First"),bd=0, highlightthickness=0)
        you_button.config(image=you_img)
        you_button.place(relx=0.26, rely=0.69, anchor=tk.CENTER)

        ai_img = Image.open('buttons_img/ai.png')
        ai_img = ai_img.resize((160,60))
        ai_img = ImageTk.PhotoImage(ai_img)
        ai_button = tk.Button(VS_AI_window,command=lambda : change_turn("Second"),bd=0, highlightthickness=0)
        ai_button.config(image=ai_img)
        ai_button.place(relx=0.517, rely=0.69, anchor=tk.CENTER)

        random_img = Image.open('buttons_img/random.png')
        random_img = random_img.resize((160,60))
        random_img = ImageTk.PhotoImage(random_img)
        RANDOM_button = tk.Button(VS_AI_window,command=lambda : change_turn("Random"),bd=0, highlightthickness=0)
        RANDOM_button.config(image=random_img)
        RANDOM_button.place(relx=0.781, rely=0.69, anchor=tk.CENTER)

        play_img = Image.open('buttons_img/play.png')
        play_img = play_img.resize((160,60))
        play_img = ImageTk.PhotoImage(play_img)
        play_button = tk.Button(VS_AI_window,  command=start_game, bd=0, highlightthickness=0)
        play_button.config(image = play_img)
        play_button.place(relx=0.51, rely=0.87, anchor=tk.CENTER)

        paramvsai_img = Image.open('buttons_img/param.png')
        paramvsai_img = paramvsai_img.resize((50,50))
        paramvsai_img = ImageTk.PhotoImage(paramvsai_img)
        paramvsai_button = tk.Button(VS_AI_window,command=lambda : parameter(VS_AI_window),bd=0, highlightthickness=0)
        paramvsai_button.config(image=paramvsai_img)
        paramvsai_button.place(relx=0.905, rely=0.11, anchor=tk.CENTER)


    # Code for starting offline game
    global offline_window, photo_offline, VSHUMAN_img, VSai_img, offlineQUIT_img, param_offline_img 
    offline_window = tk.Frame(root)
    welcome_frame.destroy()
    offline_window.pack(fill=tk.BOTH, expand=True)

    offline_img = Image.open("backgrounds/welcome.png")
    photo_offline = ImageTk.PhotoImage(offline_img)
    offline_background = tk.Label(offline_window, image=photo_offline)
    offline_background.place(x=0, y=0, relwidth=1, relheight=1) 
    
    # Create buttons for 1v1 and VSAI play
    VSHUMAN_img = Image.open('buttons_img/1_vs_1.png')
    VSHUMAN_img = VSHUMAN_img.resize((210,58))
    VSHUMAN_img = ImageTk.PhotoImage(VSHUMAN_img)
    VSHUMAN_button = tk.Button(offline_window,command=play_VSHUMAN,bd=0, highlightthickness=0)
    VSHUMAN_button.config(image=VSHUMAN_img)
    VSHUMAN_button.place(relx=0.34, rely=0.58, anchor=tk.CENTER)

    VSai_img = Image.open('buttons_img/1_vs_ai.png')
    VSai_img = VSai_img.resize((210,58))
    VSai_img = ImageTk.PhotoImage(VSai_img)
    VSai_button = tk.Button(offline_window,command=play_VSAI,bd=0, highlightthickness=0)
    VSai_button.config(image=VSai_img)
    VSai_button.place(relx=0.68, rely=0.58, anchor=tk.CENTER)

    param_offline_img = Image.open('buttons_img/param.png')
    param_offline_img = param_offline_img.resize((50,50))
    param_offline_img = ImageTk.PhotoImage(param_offline_img)
    param_offline_button = tk.Button(offline_window,command=lambda : parameter(offline_window),bd=0, highlightthickness=0)
    param_offline_button.config(image=param_offline_img)
    param_offline_button.place(relx=0.895, rely=0.1, anchor=tk.CENTER)
    
def play_online():
    # Code for handling online play
    # For example, create a new window for entering IP address and pseudo
    GLOBALS.gamemode = ONLINE
 
    # Create a new Toplevel window for online play setup

    global online_window
    online_window = tk.Toplevel(root)
    online_window.title("Online Play Setup")

    global host_guest_var
    host_guest_var = tk.StringVar(value="guest")
    IA_human_var = tk.StringVar(value="human")

    def start_online_game():
        connexion.destroy() 
        connexion.forget()
        selection = host_guest_var.get()
        selection2=IA_human_var.get()
        if selection == "host":
            GLOBALS.port = int(port_entry.get())   
            GLOBALS.pseudo = pseudo_entry.get()
            GLOBALS.ip = com.get_ip()  # For hosting, you can use localhost
            GLOBALS.socket = com.host_game(GLOBALS.ip, GLOBALS.port, GLOBALS.pseudo)
            if selection2 =="IA":
                GLOBALS.bot=2
            else:
                GLOBALS.player=2
            # Start host connection with given port and pseudo
        else:
            GLOBALS.ip = ip_entry.get()
            GLOBALS.port = int(port_entry.get())
            GLOBALS.pseudo = pseudo_entry.get()
            GLOBALS.socket = com.guest_game(GLOBALS.ip, GLOBALS.port, GLOBALS.pseudo)
            if selection2 =="IA":
                GLOBALS.bot=1
            else:
                GLOBALS.player=1    
            # Start guest connection with given ip, port, and pseudo

        welcome_frame.destroy()
        main_frame_packing()  # Start the game 
        draw_board()
        root.update()
        game_loop()

    def on_radio_select():
        selection = host_guest_var.get()
        if selection == "guest":
            ip_label.config(state=tk.NORMAL)
            ip_entry.config(state=tk.NORMAL)
            pseudo_label.config(state=tk.NORMAL)
            pseudo_entry.config(state=tk.NORMAL)
        else:
            ip_label.config(state=tk.DISABLED)
            ip_entry.config(state=tk.DISABLED)
            pseudo_label.config(state=tk.NORMAL)
            pseudo_entry.config(state=tk.NORMAL)

    
    your_ip_text = tk.Label(online_window, text="Your IP Address:" + GLOBALS.ip_perso)
    your_ip_text.pack()
    
    guest_radio = tk.Radiobutton(online_window, text="Guest", variable=host_guest_var, value="guest", command=on_radio_select)
    host_radio = tk.Radiobutton(online_window, text="Host", variable=host_guest_var, value="host", command=on_radio_select)
    guest_radio.pack()
    host_radio.pack()

    ip_label = tk.Label(online_window, text="Enter IP Address:")
    ip_label.pack()
    ip_entry = tk.Entry(online_window)
    ip_entry.pack()

    pseudo_label = tk.Label(online_window, text="Enter Pseudo:")
    pseudo_label.pack()
    pseudo_entry = tk.Entry(online_window)
    pseudo_entry.pack()

    port_label = tk.Label(online_window, text="Enter Port:")
    port_label.pack()
    port_entry = tk.Entry(online_window)
    port_entry.pack()

    human_radio = tk.Radiobutton(online_window, text="human", variable=IA_human_var, value="human", command=on_radio_select)
    IA_radio = tk.Radiobutton(online_window, text="IA", variable=IA_human_var, value="IA", command=on_radio_select)
    human_radio.pack()
    IA_radio.pack()

    # Add a button to start online play
    start_online_button = tk.Button(online_window, text="Start Online Play", command=start_online_game)
    start_online_button.pack()
    
    connexion = tk.Frame(root)
    welcome_frame.destroy()
    connexion.pack(fill=tk.BOTH, expand=True)
    conn = Image.open("backgrounds/connexion.png")
    conn = ImageTk.PhotoImage(conn)
    conn = tk.Label(connexion, image=conn)
    conn.place(x=0, y=0, relwidth=1, relheight=1)
    
# offline/online BUTTON - initialisation
offline_img = Image.open('buttons_img/offline.png')
offline_img = offline_img.resize((210,58))
offline_img = ImageTk.PhotoImage(offline_img)
offline_button = tk.Button(root,command=play_offline,bd=0, highlightthickness=0,highlightbackground=None)
offline_button.config(image=offline_img)
offline_button.place(relx=0.34, rely=0.58, anchor=tk.CENTER)

online_img = Image.open('buttons_img/online.png')
online_img = online_img.resize((210,58))
online_img = ImageTk.PhotoImage(online_img)
online_button = tk.Button(root,command=play_online,bd=0, highlightthickness=0,highlightbackground=None)
online_button.config(image=online_img)
online_button.place(relx=0.68, rely=0.58, anchor=tk.CENTER)

parameter_img = Image.open('buttons_img/param.png')
parameter_img = parameter_img.resize((50,50))
parameter_img = ImageTk.PhotoImage(parameter_img)
parameter_button = tk.Button(root,command=lambda : parameter(welcome_frame),bd=0,highlightthickness=0,highlightbackground=None)
parameter_button.config(image=parameter_img)
parameter_button.place(relx=0.895, rely=0.1, anchor=tk.CENTER)

    ######################

main_frame = tk.Frame(root)

# BOARD FRAME - creation
board_frame = tk.Frame(main_frame)
board_frame.pack(fill=tk.BOTH, expand=True)
board_img = Image.open("backgrounds/main.png")
board_img = ImageTk.PhotoImage(board_img)
board_background = tk.Label(board_frame, image=board_img)
board_background.place(x=0, y=0, relwidth=1, relheight=1)

# PLAYER ONE SKIN - user
blue_miner = Image.open("miners/blue_miner.png")
blue_miner = blue_miner.resize((90, 90))
blue_miner = ImageTk.PhotoImage(blue_miner)
blue_miner_b = tk.Button(board_background, image=blue_miner, borderwidth=0, highlightthickness=0)
blue_miner_b.place(x=257, y=648,anchor='center')


# PLAYER TWO SKIN - user2 or bot
red_miner = Image.open("miners/red_miner.png")
red_miner = red_miner.resize((90, 90))
red_miner = ImageTk.PhotoImage(red_miner)
red_miner_b = tk.Button(board_background, image=red_miner,borderwidth=0, highlightthickness=0)
red_miner_b.place(x=1126, y=648,anchor='center')

param1V1_img = Image.open('buttons_img/param.png')
param1V1_img = param1V1_img.resize((45, 45))
param1V1_img = ImageTk.PhotoImage(param1V1_img)
param1V1_button = tk.Button(board_frame,command=lambda : parameter(board_frame),bd=0, highlightthickness=0)
param1V1_button.config(image=param1V1_img)
param1V1_button.place(relx=0.928, rely=0.109, anchor=tk.CENTER)

# TEXT - defining the text area
text_area = tk.Text(board_frame,width= 20, height=0, bg="#3C0992", fg=ini.WHITE, font=('Singly Linked', 25), bd=0, highlightbackground="#10103A", borderwidth=0, highlightthickness=0)
text_area.pack(side=tk.BOTTOM,pady=10)

"""End Tkinter Initialization"""

def play_sound(soundpath: str) -> None:
    # Initialize the mixer (if not already initialized)
    if not mixer.get_init():
        mixer.init()


    # Find an available sound channel
    for channel in range(mixer.get_num_channels()):
        if not mixer.Channel(channel).get_busy():
            # Load and play the sound on the found channel
            mixer.Channel(channel).set_volume(0.5)  # Adjust volume if needed
            mixer.Channel(channel).play(mixer.Sound(soundpath))
            break
#initial positions of the miners
liste = [(257,648),(1126,648)]

def move_button(button : tk.Button, px):
    if button == 1 :
        button = blue_miner_b
        x_coord,y_coord = liste[0]
        y_coord -= px
        button.place(x = x_coord,y = y_coord)
        liste[0] = (x_coord,y_coord)
    else :
        button = red_miner_b
        x_coord,y_coord = liste[1]
        y_coord -= px
        button.place(x = x_coord,y = y_coord)
        liste[1] = (x_coord,y_coord)


def update_text() -> None:
    """Updates the text displayed on the TextArea"""
    if not GLOBALS.game_over:
            if GLOBALS.turn == 1:
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, " Blue move !\n")
                text_area.tag_configure("center", justify="center")  
                text_area.tag_add("center", "1.0", "end")
            else:
                text_area.delete("1.0", tk.END)
                text_area.insert(tk.END, "Red move !\n")
                text_area.tag_configure("center",justify="center")  
                text_area.tag_add("center", "1.0", "end")
    else:
        global line_to_write
        if GLOBALS.turn == 0:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "Draw...\n")
            text_area.tag_configure("center", justify="center")
            text_area.tag_add("center", "1.0", "end")
        elif GLOBALS.turn == 1:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "Blue won!\n")
            text_area.tag_configure("center", justify="center")
            text_area.tag_add("center", "1.0", "end")
        else:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "Red won!\n")
            text_area.tag_configure("center", justify="center") 
            text_area.tag_add("center", "1.0", "end")

l=[]
list_tic=[[0 for _ in range(3)] for _ in range(3)]
local_boards = [[[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]
list_tic_acc = [[0 for _ in range(3)] for _ in range(3)]
list_color = [ini.WHITE for i in range (9)]

def draw_board(update: bool = True) -> None:
    """Displays the full global and local boards in the GUI."""
    i=1
    # for each local board
    for outer_y in range(3):
        for outer_x in range(3):
            # get the current local board
            local_board = GLOBALS.global_board.local_board_list[outer_y*3+outer_x]
            # top left coordinate of the current local board
            board_origin_x = ini.BOARDERSIZE+55 + ((ini.LOCALBOARDSIZE + ini.WHITESPACE) * outer_x)
            board_origin_y = ini.BOARDERSIZE-210 + ((ini.LOCALBOARDSIZE + ini.WHITESPACE) * outer_y)

            # color the board accordingly if it is won by X or O, or if it is in focus
            color = ini.WHITE
            if local_board.focus and not GLOBALS.game_over:  # if the game is over, nothing is in focus
                color = ini.GRAY
            if GLOBALS.global_board.board[outer_y][outer_x] == 1:
                color = "lightblue"
            elif GLOBALS.global_board.board[outer_y][outer_x] == 2:
                color = ini.LIGHT_ORANGE 
            else : 
                color = ini.WHITE
            list_color[local_board.index] = color
            
            # draw the board rectangle
            if len(l) <9 or (GLOBALS.global_board.board[outer_y][outer_x] == 1 or GLOBALS.global_board.board[outer_y][outer_x] == 2 ) :
                board_rectangle = tk.Canvas(board_frame, bg=color, width=ini.LOCALBOARDSIZE, height=ini.LOCALBOARDSIZE, highlightthickness=6, highlightbackground=ini.BLUE)
                board_rectangle.place(x=board_origin_x, y=board_origin_y)

            # draw the grid lines for the local board
            if len(l) <9 or (GLOBALS.global_board.board[outer_y][outer_x] == 1 or GLOBALS.global_board.board[outer_y][outer_x] == 2 ) :
                l.append(board_rectangle)
                for i in range(2):
                    # Vertical Grid Lines
                    board_rectangle.create_line(50, 0, 50, ini.LOCALBOARDSIZE+2, fill=ini.BLUE,width=3)
                    board_rectangle.create_line(103, 0, 103, ini.LOCALBOARDSIZE+2, fill=ini.BLUE,width=3)
                
                    # horizontal Grid Lines          
                    board_rectangle.create_line(3, 53, ini.LOCALBOARDSIZE+2, 53, fill=ini.BLUE,width=3)
                    board_rectangle.create_line(3, 103,ini.LOCALBOARDSIZE+2, 103, fill=ini.BLUE,width=3)

            if  GLOBALS.global_board.board[outer_y][outer_x] == 1 and i == 1 and list_tic_acc[outer_y][outer_x] >= 1:
                board_rectangle.delete('all')
                ut.draw_diamond(board_rectangle,50,50,80,ini.LIGHT_BLUE,ini.MEDIUM_BLUE)
                if list_tic_acc[outer_y][outer_x] == 1:
                    play_sound("sound_effects/blue_diamond_sparkle.mp3")
                i =2
        
            elif  GLOBALS.global_board.board[outer_y][outer_x] == 2 and i == 1 and list_tic_acc[outer_y][outer_x] >= 1:
                board_rectangle.delete('all')
                ut.draw_diamond(board_rectangle,50,50,80,ini.LIGHT_ORANGE,ini.ORANGE)
                if list_tic_acc[outer_y][outer_x] == 1:
                    play_sound("sound_effects/red_diamond_sparkle.mp3")
                
                i = 3

def get_inputs(mouse: Tuple[int, int]) -> Optional[Tuple[bd.LocalBoard, int, int]]:
    """Gets the current position of the mouse and returns the local board, as well as row and column coordinates of the
    square that the mouse is currently in. If the mouse is not in a square, then local_board will return None."""

    x_pos, y_pos = mouse  # current x and y coordinates of the mouse
    # For each local board
    for x in range(3):
        for y in range(3):
            # Top left coordinate of the current local board
            board_origin_x = ini.BOARDERSIZE+67 + ((ini.LOCALBOARDSIZE + ini.WHITESPACE) * x)
            board_origin_y = ini.BOARDERSIZE-170 + ((ini.LOCALBOARDSIZE + ini.WHITESPACE) * y)
            # If the mouse is over the current local_board area, return local_board, row, and col
            if 0 <= x_pos - board_origin_x <= ini.LOCALBOARDSIZE and 0 <= y_pos - board_origin_y <= ini.LOCALBOARDSIZE:

                local_board = GLOBALS.global_board.local_board_list[y * 3 + x]
                row = (y_pos - board_origin_y) // ini.SQUARESIZE
                col = (x_pos - board_origin_x) // ini.SQUARESIZE
                return local_board, row, col

    # If the mouse was not over a local board, return None
    return None

def make_move(local_board: bd.LocalBoard, row: int, col: int) -> None:
    """Takes a local board and the coordinates of a space on the board, and marks the space for the current player. Then
    checks for global board updates and acts accordingly."""

    local_board.board[row][col] = GLOBALS.turn  # set space to player
    # Check if this move determines the outcome of the local board (win, lose, draw)

    conversion = {0:'00', 1:'10', 2:'20', 3:'01', 4:'11', 5:'21', 6:'02', 7:'12', 8:'22'}

    if local_board.has_tic_tac_toe(GLOBALS.turn) :
        for i in range(3) :
            for j in range (3) : 
                if list_tic_acc[i][j] != 0 :
                    list_tic_acc[i][j] += 1
        list_tic_acc [local_board.index//3][local_board.index%3] = 1
        list_tic[local_board.index//3][local_board.index%3]= GLOBALS.turn
        if list_tic_acc [local_board.index//3][local_board.index%3] == 1 and not GLOBALS.global_board.has_tic_tac_toe(GLOBALS.turn):
            move_button(GLOBALS.turn,50)
        # if local board has been won, set playable to False, then mark the global board
        local_board.playable = False
        GLOBALS.lb_state[conversion[local_board.index]] = 1 
        GLOBALS.global_board.mark_global_board(local_board, GLOBALS.turn)
        draw_board()


        # Now check if this determines the outcome of the global board. If so, the game is over
        if GLOBALS.global_board.has_tic_tac_toe(GLOBALS.turn):
            while liste[GLOBALS.turn-1][1]>320 : 
                move_button(GLOBALS.turn,1)
            
            move_button(GLOBALS.turn,50)
 
            GLOBALS.game_over = True
        elif GLOBALS.global_board.is_full():

            GLOBALS.game_over = True
            GLOBALS.turn = 0

    # if the local board is a draw
    elif local_board.is_full():

        local_board.playable = False
        GLOBALS.lb_state[conversion[local_board.index]] = 1
        GLOBALS.global_board.mark_global_board(local_board, -1)
        list_tic[local_board.index//3][local_board.index%3]= GLOBALS.turn
        
        if GLOBALS.global_board.is_full():

            GLOBALS.game_over = True

    # update the focus of the local boards for the next turn
    #GLOBALS.global_board.update_focus(row, col)

    # switch player 1 <-> 2
    if not GLOBALS.game_over:
  
        GLOBALS.prev_turn = GLOBALS.turn
        GLOBALS.turn = (GLOBALS.turn % 2) + 1

    # draw
    saved_i=12
    if GLOBALS.turn == 2:
        if list_tic_acc[local_board.index//3][local_board.index%3] == 1 :
            list_tic_acc [local_board.index//3][local_board.index%3] += 1
        local_boards[local_board.index//3][local_board.index%3][row][col] = 2
        ut.draw_diamond(l[local_board.index],ini.SQUARESIZE*(col)+30, ini.SQUARESIZE*(row)+30, ini.SQUARESIZE // 3,ini.LIGHT_BLUE,ini.MEDIUM_BLUE)
        play_sound("sound_effects/blue_miner_shovel.mp3")
        update_text()

    else :
        if list_tic_acc[local_board.index//3][local_board.index%3] == 1 :
            list_tic_acc [local_board.index//3][local_board.index%3] += 1
        local_boards[local_board.index//3][local_board.index%3][row][col] = 1
        ut.draw_diamond(l[local_board.index],ini.SQUARESIZE*(col)+30, ini.SQUARESIZE*(row)+30, ini.SQUARESIZE // 3,ini.LIGHT_RED,ini.ORANGE)
        play_sound("sound_effects/red_miner_shovel.mp3")
        update_text()
    
    if GLOBALS.game_over :
        pass
                
    else :
        for i in range(9):
            if i == col+row*3:
                if list_tic[i//3][i%3] != 0 :
                    saved_i = i
       
                l[i].configure(bg=ini.WHITE)
                        
                if not GLOBALS.global_board.local_board_list[i].has_tic_tac_toe(GLOBALS.turn) :
                    GLOBALS.global_board.local_board_list[i].playable=True
                    GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[i]
                            
            else :
                l[i].configure(bg=ini.MEDIUM_GRAY)
                GLOBALS.global_board.local_board_list[i].playable=False
        if saved_i !=12 :
      
            for i in range(9):
                #if i != saved_i and not GLOBALS.global_board.local_board_list[i].has_tic_tac_toe(GLOBALS.turn) :
                if i != saved_i :
                    GLOBALS.global_board.local_board_list[i].playable=True
                    GLOBALS.lb_for_hand = GLOBALS.global_board.local_board_list[i]
                    l[i].configure(bg=ini.WHITE)
                    GLOBALS.global_board.local_board_list[i].focus = True
                    for j in range (9) : 
                        if j != i :
                            GLOBALS.global_board.local_board_list[i].focus =  True
            saved_i = 12

def handle_mouse_click(event):
    """Handle mouse click event"""
    # Get the mouse coordinates
    window_x = root.winfo_rootx()
    window_y = root.winfo_rooty()
    mouse = (event.x_root-window_x, event.y_root-window_y+30)
    # get lb, and row and col coordinates from get_inputs(). Check if lb is None
    params = get_inputs(mouse)      
    if params is not None:
        lb, row, col = params
        # check if local board is in focus, playable, and if selected space has not yet been played
        if lb.focus and lb.playable and lb.board[row][col] == 0:
            if GLOBALS.gamemode == ONLINE:
                play = str(lb.index)+str(row*3+col)
                com.send_play(GLOBALS.socket, play, GLOBALS.state_of_play, GLOBALS.turn)
            make_move(lb, row, col)
            GLOBALS.prev_local_row, GLOBALS.prev_local_col = row, col
            GLOBALS.prev_lb=lb
            var.set(1)

def game_loop():

    GLOBALS.game_over = False
    while True :
        if not GLOBALS.game_over :

            if GLOBALS.gamemode == VS_AI:   # Mode Human VS AI
                if GLOBALS.turn == GLOBALS.bot :  # bot turn
                    if GLOBALS.bot_difficulty == 'Easy' :
                        if local_boards == [[[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]:
                            GLOBALS.prev_local_row, GLOBALS.prev_local_col = None, None
                            lb,row,col=GLOBALS.global_board.local_board_list[4],1,1
                        else:
                            eval,move = al.alpha_beta_pruning(local_boards, 5, -float('inf'), float('inf'), True, GLOBALS.prev_local_row, GLOBALS.prev_local_col,5)
                            grow,gcol,lrow,lcol = move
                            lb, row, col = GLOBALS.global_board.local_board_list[gcol + grow*3],lrow,lcol
                    
                    elif GLOBALS.bot_difficulty == 'Medium':
                        if local_boards == [[[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]:
                            GLOBALS.prev_local_row, GLOBALS.prev_local_col = None, None
                            lb,row,col=GLOBALS.global_board.local_board_list[4],1,1
                        else:
                            box_won = alV5.update_box_won(local_boards)
                            _,move1=alV5.minimax(local_boards,GLOBALS.prev_lb.index,GLOBALS.prev_local_row,GLOBALS.prev_local_col,str(GLOBALS.bot),3,box_won)  
                            lb, row, col = GLOBALS.global_board.local_board_list[move1[0]],move1[1],move1[2]

                    elif GLOBALS.bot_difficulty == 'Hard' :
                        depth=5
                        if local_boards == [[[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]:
                            GLOBALS.prev_local_row, GLOBALS.prev_local_col = None, None
                            lb,row,col=GLOBALS.global_board.local_board_list[4],1,1                        
                        else:
                            valid_moves = [(i, j, x, y) for i in range(3) for j in range(3) for x in range(3) for y in range(3)
                            if al.is_valid_move(list_tic, local_boards, i, j, x, y, GLOBALS.prev_local_row, GLOBALS.prev_local_col)]

                            if not valid_moves:
                                valid_moves = [(i, j, x, y) for i in range(3) for j in range(3) for x in range(3) for y in range(3) if al.is_valid_move_2(list_tic, local_boards, i, j, x, y)]
                            for move in valid_moves:
                                newlt = [[[[i for i in local_boards[l][k][j]]for j in range (len(local_boards[l][k]))]for k in range (len(local_boards[l]))]for l in range (len(local_boards))]

                                gbbrd = [[list_tic[i][j] for i in range(3)] for j in range(3)]
                                global_row, global_col, local_row, local_col = move
                                newlt[move[0]][move[1]][move[2]][move[3]] = 1
                                if al.check_local_board_win(newlt[global_row][global_col], 1):
                                    gbbrd[global_row][global_col] = 1
                                if al.check_global_board_win(newlt,1):
                                    lb, row, col = GLOBALS.global_board.local_board_list[gcol + grow*3],lrow,lcol
                                    make_move(lb, row, col)

                            box_won = alV5.update_box_won(local_boards)
                            valid_moves = [(i, j, x, y) for i in range(3) for j in range(3) for x in range(3) for y in range(3) if al.is_valid_move(list_tic, local_boards, i, j, x, y, GLOBALS.prev_local_row, GLOBALS.prev_local_col)]
                            if not valid_moves:
                                _,move1=alV5.minimax(local_boards,GLOBALS.prev_lb.index,GLOBALS.prev_local_row,GLOBALS.prev_local_col,str(GLOBALS.bot),3,box_won)
                            else:
                                
                                _,move1=alV5.minimax(local_boards,GLOBALS.prev_lb.index,GLOBALS.prev_local_row,GLOBALS.prev_local_col,str(GLOBALS.bot),depth,box_won)

                            lb, row, col = GLOBALS.global_board.local_board_list[move1[0]],move1[1],move1[2]
                    make_move(lb, row, col)  # record the move and update the GUI

                else:   # Human turn
                    update_text()
                    if GLOBALS.lb_for_hand == None:
                        root.bind("<Button-1>", handle_mouse_click)
                    else:
                        root.bind("<<cell_selected>>", handle_mouse_click)
                    root.wait_variable(var)
            if GLOBALS.gamemode == TWO_PLAYERS:   # Mode Local
                update_text()
                if GLOBALS.lb_for_hand == None:
                    root.bind("<Button-1>", handle_mouse_click)
           
                else:
                    root.bind("<<cell_selected>>", handle_mouse_click)
                root.wait_variable(var)
                draw_board()
                root.update()

            if GLOBALS.gamemode == ONLINE: # Mode online
                GLOBALS.state_of_play = com.convert_to_string(GLOBALS.global_board)
                update_text()
                if GLOBALS.turn == GLOBALS.player: # Local player turn
                    if GLOBALS.lb_for_hand == None:
                        root.bind("<Button-1>", handle_mouse_click)
                    else:
                        root.bind("<<cell_selected>>", handle_mouse_click)
                    root.wait_variable(var)
                
                elif GLOBALS.turn == GLOBALS.bot :
                    if local_boards == [[[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]:
                        GLOBALS.prev_local_row, GLOBALS.prev_local_col = None, None
                        lb,row,col=GLOBALS.global_board.local_board_list[4],1,1  
                    else :
                        box_won = alV5.update_box_won(local_boards)
                        valid_moves = [(i, j, x, y) for i in range(3) for j in range(3) for x in range(3) for y in range(3) if al.is_valid_move(list_tic, local_boards, i, j, x, y, GLOBALS.prev_local_row, GLOBALS.prev_local_col)]
                        if not valid_moves:
                            _,move1=alV5.minimax(local_boards,GLOBALS.prev_lb.index,GLOBALS.prev_local_row,GLOBALS.prev_local_col,str(GLOBALS.bot),3,box_won)
                        else:
                            _,move1=alV5.minimax(local_boards,GLOBALS.prev_lb.index,GLOBALS.prev_local_row,GLOBALS.prev_local_col,str(GLOBALS.bot),depth,box_won)                       
                        lb, row, col = GLOBALS.global_board.local_board_list[move1[0]],move1[1],move1[2]
                    play = str(lb.index)+str(row*3+col)
                    com.send_play(GLOBALS.socket, play, GLOBALS.state_of_play, GLOBALS.turn)
                    make_move(lb, row, col)  
                    
                else:
                    play = com.get_play(GLOBALS.socket, GLOBALS.state_of_play, GLOBALS.turn)
                    lb = GLOBALS.global_board.local_board_list[int(play[0])]
                    row = int(play[1])//3
                    col = int(play[1])%3
                    make_move(lb, row, col)
                    GLOBALS.prev_lb=lb
                    GLOBALS.prev_local_row = row
                    GLOBALS.prev_local_col = col

            root.update()

        else:
            if GLOBALS.gamemode == ONLINE:
                com.end_game(GLOBALS.socket, GLOBALS.turn, GLOBALS.player, GLOBALS.bot, GLOBALS.prev_turn)
            break
        



# handle other events, such as new game, quit, etc.

def handle_new_game(event):

    GLOBALS.reset = True

def main() -> None:

    root.mainloop()

# START OF GUI
main()

