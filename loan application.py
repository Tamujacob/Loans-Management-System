from tkinter import *
from tkinter import ttk


window=Tk()
window.title("Apply For A Loan")
window.geometry("800x600")
window.configure(bg="#e1ffc9")

title_label=Label(window,text="APPLY FOR A LOAN",font=("Arial",25,"bold"),bg="#e1ffc9")
title_label.pack(pady=20)

widget_frame=Frame(window,bg="white", padx=20, pady=20, relief="raised", bd=3)
widget_frame.pack()

name_label=Label(widget_frame,text="Full Name:",font=("Arial"))
name_label.grid(row=0,column=0,padx=5,pady=5,sticky=W)
name_entry=Entry(widget_frame,font=("Arial"),width=30)
name_entry.grid(row=0,column=1,padx=5,pady=5)

amount_label=Label(widget_frame,text="Loan Amount:",font=("Arial"))
amount_label.grid(row=1,column=0,padx=5,pady=5,sticky=W)
amount_entry=Entry(widget_frame,font=("Arial"),width=30)
amount_entry.grid(row=1,column=1,padx=5,pady=5)

type_label=Label(widget_frame,text="Loan type",font=("Arial"))
type_label.grid(row=2,column=0,padx=5,pady=5,sticky=W)
type_combo = ttk.Combobox(widget_frame, values=["Personal Loan", "Business Loan", "Car Loan", "Home Loan","School Fees Loan"], font=("Arial", 12))
type_combo.grid(row=2, column=1, pady=5)

duration_label=Label(widget_frame,text="Repayment Duration",font=("Arial"))
duration_label.grid(row=3,column=0,padx=5,pady=5,sticky=W)
duration_combo = ttk.Combobox(widget_frame, values=["6 months", "1 year", "2 years", "3 years","5 years"], font=("Arial", 12))
duration_combo.grid(row=3, column=1, pady=5,sticky=W)

method_label=Label(widget_frame,text="Repayment Method",font=("Arial"))
method_label.grid(row=4, column=0, pady=5,sticky=W)
monthly_radio=Radiobutton(widget_frame, text="Monthly", value="Monthly", font=("Arial"))
monthly_radio.grid(row=4, column=1, pady=5, sticky="w")
weekly_radio = Radiobutton(widget_frame, text="Weekly", value="Weekly", font=("Arial"))
weekly_radio.grid(row=4, column=2, pady=5, sticky="w")

purpose_label=Label(widget_frame,text="Loan purpose:", font=("Arial", 12), bg="white")
purpose_label.grid(row=5,column=0,sticky="w",pady=5)
loan_purpose_text = Text(widget_frame, height=3, width=30, font=("Arial", 12))
loan_purpose_text.grid(row=5, column=1, pady=5)

security_label=Label(widget_frame,text="Collateral Security:", font=("Arial", 12))
security_label.grid(row=6, column=0, sticky="w", pady=5)
collateral_entry = Entry(widget_frame, font=("Arial", 12), width=30)
collateral_entry.grid(row=6, column=1, pady=5)

return_label=Label(widget_frame,text="Return Amount:", font=("Arial", 12), bg="white")
return_label.grid(row=7, column=0, sticky="w", pady=5)
return_amount_entry = Entry(widget_frame, font=("Arial", 12), width=30, state="readonly")
return_amount_entry.grid(row=7, column=1, pady=5)

terms_var = IntVar()
terms_check = Checkbutton(widget_frame, text="I accept the terms and conditions", variable=terms_var, font=("Arial", 12), bg="white")
terms_check.grid(row=8, columnspan=2, pady=10)

btn_frame = Frame(window, bg="#e1ffc9")
btn_frame.pack(pady=10)

submit_btn = Button(btn_frame, text="Submit Application", bg="#28a745", fg="white", font=("Arial", 12, "bold"), width=18)
submit_btn.grid(row=0, column=0, padx=10)

clear_btn = Button(btn_frame, text="Clear", bg="#dc3545", fg="white", font=("Arial", 12, "bold"), width=10)
clear_btn.grid(row=0, column=1, padx=10)
window.mainloop() 