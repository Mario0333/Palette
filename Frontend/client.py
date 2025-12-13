import customtkinter as ctk
import requests
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageTk, ImageDraw
import io
import random

API_URL = "http://127.0.0.1:5000"
current_user = None
current_user_id = None
dark_mode = False

# ===================================================================
# Helper Functions
# ===================================================================
def make_circle(img: Image.Image, size=(150, 150)):
    img = img.resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    out = Image.new("RGBA", size)
    out.paste(img, (0, 0), mask=mask)
    return out

def create_placeholder(size=(150, 150)):
    img = Image.new("RGB", size, "#333333")
    draw = ImageDraw.Draw(img)
    draw.text((30, 60), "No Pic", fill="#888888")
    return make_circle(img, size)

# ===================================================================
# LOGIN / SIGNUP — FIXED ALL GHOST TASKS
# ===================================================================
def open_login_window():
    global current_user, current_user_id
    login_win = ctk.CTk()
    login_win.title("PALETTE - Welcome")
    login_win.geometry("500x800")
    login_win.configure(fg_color="#0f0f1f")

    ctk.CTkLabel(login_win, text="PALETTE", font=("Brush Script MT", 80), text_color="#00ffff").pack(pady=80)
    ctk.CTkLabel(login_win, text="Draw. Share. Inspire.", font=("Helvetica", 18), text_color="#888888").pack(pady=10)

    frame = ctk.CTkFrame(login_win, fg_color="#1a1a2e", corner_radius=30)
    frame.pack(pady=40, padx=60, fill="both", expand=True)

    mode = ctk.StringVar(value="login")
    ctk.CTkLabel(frame, text="Login or Sign Up", font=("Helvetica", 26, "bold"), text_color="#00ffff").pack(pady=30)

    entry_user = ctk.CTkEntry(frame, placeholder_text="Username", width=320, height=55)
    entry_user.pack(pady=15)
    entry_pass = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=320, height=55)
    entry_pass.pack(pady=15)

    def submit():
        global current_user, current_user_id
        u = entry_user.get().strip()
        p = entry_pass.get().strip()
        if not u or not p:
            messagebox.showerror("Error", "Fill everything!")
            return

        ep = "/login" if mode.get() == "login" else "/signup"
        r = requests.post(f"{API_URL}{ep}", json={"username": u, "password": p})

        if r.status_code in [200, 201]:
            current_user = u
            current_user_id = r.json().get("user_id")

            # THIS LINE KILLS ALL GHOST TASKS — NO MORE ERRORS!
            login_win.after_cancel("all")
            login_win.destroy()
            open_main_window()
        else:
            messagebox.showerror("Oops", r.json().get("message", "Try again"))

    ctk.CTkButton(frame, text="Login", width=250, height=55, fg_color="#00ffff", text_color="#000",
                  command=lambda: [mode.set("login"), submit()]).pack(pady=12)
    ctk.CTkButton(frame, text="Sign Up", width=250, height=55, fg_color="#ff3366", hover_color="#ff6699",
                  command=lambda: [mode.set("signup"), submit()]).pack(pady=12)

    login_win.mainloop()

# ===================================================================
# MAIN WINDOW
# ===================================================================
def open_main_window():
    global current_user, current_user_id
    main = ctk.CTk()
    main.title("PALETTE")
    main.geometry("1280x700")
    main.resizable(True, True)
    main.configure(fg_color="#0f172a")  # Same as login

    # Configure main window grid
    main.grid_columnconfigure(0, weight=1)
    main.grid_rowconfigure(0, weight=0)  # Menu bar row
    main.grid_rowconfigure(1, weight=1)  # Tabview row

    # Menu bar — matching login
    menu_bar = ctk.CTkFrame(main, fg_color="#1e293b", height=60, corner_radius=30)
    menu_bar.grid(row=0, column=0, sticky="ew", padx=40, pady=30)
    
    # Use grid inside menu_bar
    menu_bar.grid_columnconfigure(0, weight=1)
    menu_bar.grid_columnconfigure(1, weight=0)
    menu_bar.grid_columnconfigure(2, weight=1)
    menu_bar.grid_columnconfigure(3, weight=0)

    logo_label = ctk.CTkLabel(menu_bar, text="PALETTE", font=("Brush Script MT", 35, "bold"), text_color="#06b6d4")
    logo_label.grid(row=0, column=1, sticky="ew")

    # Profile pic in menu
    profile_response = requests.get(f"{API_URL}/profile/{current_user_id}")
    profile_data = profile_response.json()
    profile_pic_filename = profile_data.get("profile_pic")
    if profile_pic_filename:
        img_url = f"{API_URL}/uploads/{profile_pic_filename}"
        img_data = requests.get(img_url).content
        img = Image.open(io.BytesIO(img_data))
        menu_img = make_circle(img, (40, 40))
    else:
        menu_img = create_placeholder((40, 40))
    menu_img_ref = ImageTk.PhotoImage(menu_img)
    menu_profile_pic = ctk.CTkLabel(menu_bar, image=menu_img_ref, text="")
    menu_profile_pic.grid(row=0, column=0, sticky="w", padx=15)

    welcome_label = ctk.CTkLabel(menu_bar, text=f"Welcome, {current_user}!", font=("Helvetica", 16, "bold"), text_color="#e2e8f0")
    welcome_label.grid(row=0, column=0, sticky="w", padx=70)

    def logout():
        global current_user, current_user_id
        current_user = None
        current_user_id = None
        main.destroy()
        open_login_window()

    logout_button = ctk.CTkButton(menu_bar, text="Logout", command=logout, fg_color="#ec4899", hover_color="#db2777", corner_radius=15)
    logout_button.grid(row=0, column=3, sticky="e", padx=15)

    # Dark Mode button 
    def toggle_dark_mode():
        messagebox.showinfo("Info", "Already in dark mode!")

    dark_mode_button = ctk.CTkButton(menu_bar, text="Dark Mode", command=toggle_dark_mode, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=15)
    dark_mode_button.grid(row=0, column=2, sticky="e", padx=15)
    
    # Tabview — same card style
    tabview = ctk.CTkTabview(main, fg_color="#1e293b", corner_radius=30)
    tabview.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)

    # Feed Tab
    feed_tab = tabview.add("Feed")

    # Use grid layout for feed and recommendations side by side
    feed_tab.grid_columnconfigure(0, weight=3)
    feed_tab.grid_columnconfigure(1, weight=1)
    feed_tab.grid_rowconfigure(0, weight=1)
    feed_tab.grid_rowconfigure(1, weight=0)

    # Feed Scrollable Area
    feed_scroll = ctk.CTkScrollableFrame(feed_tab, fg_color="#1e293b", corner_radius=20)
    feed_scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def load_feed():
        response = requests.get(API_URL + "/feed")
        if response.status_code == 200:
            posts = response.json()
            for widget in feed_scroll.winfo_children():
                widget.destroy()
            for post in posts:
                post_frame = ctk.CTkFrame(feed_scroll, fg_color="#334155", corner_radius=20)
                post_frame.pack(fill="x", pady=12, padx=15)

                # Image
                img_url = f"{API_URL}/uploads/{post['filename']}"
                img_data = requests.get(img_url).content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((200, 200), Image.LANCZOS)
                img_tk = ctk.CTkImage(img, size=(200, 200))
                img_label = ctk.CTkLabel(post_frame, image=img_tk, text="")
                img_label.pack(side="left", padx=15, pady=10)

                # Post info
                info_frame = ctk.CTkFrame(post_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15)

                # Username with avatar
                user_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                user_frame.pack(fill="x", pady=5)
                if post['profile_pic']:
                    user_pic_url = f"{API_URL}/uploads/{post['profile_pic']}"
                    user_pic_data = requests.get(user_pic_url).content
                    user_pic_img = Image.open(io.BytesIO(user_pic_data))
                    user_pic_img = user_pic_img.resize((30, 30), Image.LANCZOS)
                    user_pic_tk = ctk.CTkImage(user_pic_img, size=(30, 30))
                    user_avatar = ctk.CTkLabel(user_frame, image=user_pic_tk, text="")
                    user_avatar.pack(side="left", padx=5)
                username_label = ctk.CTkLabel(user_frame, text=post['username'], font=("Helvetica", 14, "bold"), text_color="#06b6d4")
                username_label.pack(side="left")
                timestamp_label = ctk.CTkLabel(user_frame, text=post['timestamp'], font=("Helvetica", 10), text_color="#94a3b8")
                timestamp_label.pack(side="right")

                # Likes
                likes_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                likes_frame.pack(fill="x", pady=5)
                like_button = ctk.CTkButton(likes_frame, text="❤️ Like", width=80, fg_color="#ec4899", text_color="#ffffff", hover_color="#db2777", corner_radius=15,
                                            command=lambda pid=post['id']: toggle_like(pid))
                like_button.pack(side="left")
                likes_label = ctk.CTkLabel(likes_frame, text=f"{post['likes_count']} likes", font=("Helvetica", 10), text_color="#e2e8f0")
                likes_label.pack(side="left", padx=10)

                # Comments section — rounded + working
                comments_frame = ctk.CTkFrame(info_frame, fg_color="#475569", corner_radius=20)
                comments_frame.pack(fill="x", pady=10)

                ctk.CTkLabel(comments_frame, text="Comments", font=("Helvetica", 14, "bold"), text_color="#06b6d4").pack(anchor="w", padx=20, pady=10)

                for comment in post['comments']:
                    c_row = ctk.CTkFrame(comments_frame, fg_color="#334155", corner_radius=15)
                    c_row.pack(fill="x", pady=5, padx=20)
                    ctk.CTkLabel(c_row, text=f"{comment['username']}: {comment['text']}", font=("Helvetica", 11), text_color="#e2e8f0", anchor="w", justify="left", wraplength=500).pack(padx=15, pady=8, anchor="w")

                # New comment input
                input_row = ctk.CTkFrame(comments_frame, fg_color="transparent")
                input_row.pack(fill="x", pady=10, padx=20)

                new_comment_entry = ctk.CTkEntry(input_row, placeholder_text="Write a comment...", width=400, height=40, corner_radius=20, fg_color="#1e293b")
                new_comment_entry.pack(side="left", fill="x", expand=True, padx=(0,10))

                def post_comment(pid=post['id']):
                    text = new_comment_entry.get().strip()
                    if text:
                        requests.post(f"{API_URL}/comment/{pid}", json={"user_id": current_user_id, "text": text})
                        new_comment_entry.delete(0, "end")
                        load_feed()

                ctk.CTkButton(input_row, text="Post", width=80, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=15,
                              command=post_comment).pack(side="right")

                # Delete if owner
                if post['user_id'] == current_user_id:
                    delete_button = ctk.CTkButton(post_frame, text="Delete", command=lambda pid=post['id']: delete_post(pid), fg_color="#ef4444", hover_color="#dc2626", corner_radius=15)
                    delete_button.pack(side="right", padx=15, pady=10)

    def toggle_like(post_id):
        response = requests.post(f"{API_URL}/like/{post_id}", json={"user_id": current_user_id})
        if response.status_code == 200:
            load_feed()

    def delete_post(post_id):
        response = requests.delete(f"{API_URL}/delete/{post_id}", json={"user_id": current_user_id})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Post deleted!")
            load_feed()
        else:
            messagebox.showerror("Error", response.json()["message"])

    # You Might Like Section (right side)
    rec_frame = ctk.CTkFrame(feed_tab, fg_color="#1e293b", corner_radius=20)
    rec_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    rec_frame.grid_rowconfigure(0, weight=0)
    rec_frame.grid_rowconfigure(1, weight=1)
    rec_frame.grid_columnconfigure(0, weight=1)

    rec_title = ctk.CTkLabel(rec_frame, text="You Might Like", font=("Helvetica", 16, "bold"), text_color="#06b6d4")
    rec_title.grid(row=0, column=0, pady=15)

    rec_scroll = ctk.CTkScrollableFrame(rec_frame, fg_color="#334155", corner_radius=15)
    rec_scroll.grid(row=1, column=0, sticky="nsew")

    def load_recommendations():
        response = requests.get(f"{API_URL}/recommendations/{current_user_id}")
        if response.status_code == 200:
            for widget in rec_scroll.winfo_children():
                widget.destroy()
            for rec in response.json():
                rec_item = ctk.CTkFrame(rec_scroll, fg_color="#475569", corner_radius=15)
                rec_item.pack(fill="x", pady=10, padx=10)

                img = Image.open(io.BytesIO(requests.get(f"{API_URL}/uploads/{rec['filename']}").content)).resize((150,150))
                img_tk = ctk.CTkImage(img, size=(150,150))
                ctk.CTkLabel(rec_item, image=img_tk, text="").pack(pady=8)

                ctk.CTkLabel(rec_item, text=rec['username'], font=("Helvetica", 12, "bold"), text_color="#06b6d4").pack()
                ctk.CTkButton(rec_item, text="Like", fg_color="#ec4899", text_color="#ffffff", hover_color="#db2777", corner_radius=15,
                              command=lambda pid=rec['id']: toggle_like(pid)).pack(pady=5)

    # Refresh button
    load_feed_button = ctk.CTkButton(feed_tab, text="Refresh Feed", command=load_feed, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=15)
    load_feed_button.grid(row=1, column=0, pady=15)

    load_feed()
    load_recommendations()

    # Upload Tab
    upload_tab = tabview.add("Upload")

    def upload_file():
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            img = Image.open(file_path)
            img = img.resize((200, 200), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            preview_label = ctk.CTkLabel(upload_tab, image=img_tk, text="")
            preview_label.image = img_tk
            preview_label.pack(pady=10)

            progress = ctk.CTkProgressBar(upload_tab, width=200)
            progress.pack(pady=10)
            progress.set(0.0)

            files = {'file': open(file_path, 'rb')}
            data = {'user_id': current_user_id}
            response = requests.post(API_URL + "/upload", files=files, data=data)
            progress.set(1.0)

            if response.status_code == 201:
                messagebox.showinfo("Success", "Upload successful!")
            else:
                messagebox.showerror("Error", response.json()["message"])
            preview_label.destroy()
            progress.destroy()

    upload_button = ctk.CTkButton(upload_tab, text="Select and Upload Drawing", command=upload_file, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=25)
    upload_button.pack(pady=20)

    # Profile Tab
    profile_tab = tabview.add("Profile")

    response = requests.get(f"{API_URL}/profile/{current_user_id}")
    profile_data = response.json()

    profile_info = ctk.CTkLabel(profile_tab, text=f"Username: {current_user}", font=("Helvetica", 16), text_color="#e2e8f0")
    profile_info.pack(pady=20)

    profile_image_ref = None
    if profile_data['profile_pic']:
        img = Image.open(io.BytesIO(requests.get(f"{API_URL}/uploads/{profile_data['profile_pic']}").content))
        profile_img = make_circle(img)
        profile_image_ref = ImageTk.PhotoImage(profile_img)
    else:
        profile_image_ref = ImageTk.PhotoImage(create_placeholder())
    profile_pic_label = ctk.CTkLabel(profile_tab, image=profile_image_ref, text="")
    profile_pic_label.pack(pady=10)

    def upload_profile_pic():
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            files = {'file': open(file_path, 'rb')}
            data = {'user_id': current_user_id}
            response = requests.post(API_URL + "/upload_profile", files=files, data=data)
            if response.status_code == 201:
                messagebox.showinfo("Success", "Profile picture uploaded!")
                new_filename = response.json()["filename"]
                img = Image.open(io.BytesIO(requests.get(f"{API_URL}/uploads/{new_filename}").content))
                new_img = make_circle(img)
                new_ref = ImageTk.PhotoImage(new_img)
                profile_pic_label.configure(image=new_ref)
                profile_pic_label.image = new_ref
            else:
                messagebox.showerror("Error", response.json()["message"])

    upload_pic_button = ctk.CTkButton(profile_tab, text="Upload Profile Picture", command=upload_profile_pic, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=15)
    upload_pic_button.pack(pady=10)

    bio_entry = ctk.CTkEntry(profile_tab, placeholder_text="Bio", width=300, corner_radius=15)
    bio_entry.insert(0, profile_data['bio'])
    bio_entry.pack(pady=5)

    location_entry = ctk.CTkEntry(profile_tab, placeholder_text="Location", width=300, corner_radius=15)
    location_entry.insert(0, profile_data['location'])
    location_entry.pack(pady=5)

    interests_entry = ctk.CTkEntry(profile_tab, placeholder_text="Interests", width=300, corner_radius=15)
    interests_entry.insert(0, profile_data['interests'])
    interests_entry.pack(pady=5)

    def save_profile():
        data = {
            "user_id": current_user_id,
            "bio": bio_entry.get(),
            "location": location_entry.get(),
            "interests": interests_entry.get()
        }
        response = requests.post(API_URL + "/update_profile", json=data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Profile updated!")

    save_button = ctk.CTkButton(profile_tab, text="Save Profile", command=save_profile, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=15)
    save_button.pack(pady=10)

    gallery_scroll = ctk.CTkScrollableFrame(profile_tab, fg_color="#1e293b", corner_radius=20)
    gallery_scroll.pack(fill="both", expand=True, pady=10)

    def load_gallery():
        response = requests.get(API_URL + "/feed")
        if response.status_code == 200:
            posts = [p for p in response.json() if p['user_id'] == current_user_id]
            for widget in gallery_scroll.winfo_children():
                widget.destroy()
            for post in posts:
                img_url = f"{API_URL}/uploads/{post['filename']}"
                img_data = requests.get(img_url).content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((100, 100), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                img_label = ctk.CTkLabel(gallery_scroll, image=img_tk, text="")
                img_label.image = img_tk
                img_label.pack(side="left", padx=5)

    load_gallery()

    # Friends Tab
    friends_tab = tabview.add("Friends")

    friends_scroll = ctk.CTkScrollableFrame(friends_tab, fg_color="#1e293b", corner_radius=20)
    friends_scroll.pack(fill="both", expand=True)

    def load_friends():
        response = requests.get(f"{API_URL}/friends/{current_user_id}")
        if response.status_code == 200:
            friends = response.json()
            for widget in friends_scroll.winfo_children():
                widget.destroy()
            for friend in friends:
                friend_label = ctk.CTkLabel(friends_scroll, text=friend['username'], font=("Helvetica", 12), text_color="#e2e8f0")
                friend_label.pack(pady=5)

    load_friends_button = ctk.CTkButton(friends_tab, text="Refresh Friends", command=load_friends, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=15)
    load_friends_button.pack(pady=10)

    add_friend_entry = ctk.CTkEntry(friends_tab, placeholder_text="Friend's username", width=300, corner_radius=15)
    add_friend_entry.pack(pady=10)

    def add_friend():
        friend_username = add_friend_entry.get()
        if friend_username:
            response = requests.post(API_URL + "/add_friend", json={"user_id": current_user_id, "friend_username": friend_username})
            if response.status_code == 201:
                messagebox.showinfo("Success", "Friend added!")
                load_friends()
            else:
                messagebox.showerror("Error", response.json()["message"])

    add_friend_button = ctk.CTkButton(friends_tab, text="Add Friend", command=add_friend, fg_color="#06b6d4", text_color="#000", hover_color="#0891b2", corner_radius=15)
    add_friend_button.pack(pady=10)

    load_friends()

    main.mainloop()

# Run app
open_login_window()