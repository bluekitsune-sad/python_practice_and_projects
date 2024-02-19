import sys
# Setup Color Options
def red(skk): sys.stdout.write("\033[91m {}\033[00m" .format(skk))
def green(skk): sys.stdout.write("\033[92m {}\033[00m" .format(skk))
def yellow(skk): sys.stdout.write("\033[93m {}\033[00m" .format(skk))
def lightpurple(skk): sys.stdout.write("\033[94m {}\033[00m" .format(skk))
def purple(skk): sys.stdout.write("\033[95m {}\033[00m" .format(skk))
def cyan(skk): sys.stdout.write("\033[96m {}\033[00m" .format(skk))
def lightgray(skk): sys.stdout.write("\033[97m {}\033[00m" .format(skk))

# Setup formatting options
def bold(type): sys.stdout.write("\033[1m" + type + "\033[0m")
def italic(type): sys.stdout.write("\033[3m" + type + "\033[0m")
def underline(type): sys.stdout.write("\033[4m" + type + "\033[0m")
def highlight(type): sys.stdout.write("\033[7m" + type + "\033[0m")
def crossout(type): sys.stdout.write("\033[9m" + type + "\033[0m")
def invisible(type): sys.stdout.write("\033[8m" + type + "\033[0m")

# Setup basic formatting options
def style(style): # When you contact any of these, the next text printed out will be in the format you select
  if style.lower() == "bold":
   sys.stdout.write("\033[1m")
  if style.lower() == "underline":
   sys.stdout.write("\033[4m")
  if style.lower() == "italic":
   sys.stdout.write("\033[3m")
  if style.lower() == "crossout":
   sys.stdout.write("\033[9m")
  if style.lower() == "highlight":
   sys.stdout.write("\033[7m")
  if style.lower() == "invisible":
   sys.stdout.write("\033[8m")
  if style.lower() == "norm" or style.lower() == "normal" or style.lower() == "reg" or style.lower() == "regular":
   sys.stdout.write("\033[0m")


red("This is red text\n")
green("This is green text\n")
yellow("This is yellow text\n")
lightpurple("This is light purple text\n")
purple("This is purple text\n")
cyan("This is cyan text\n")
lightgray("This is light gray text\n")

bold("This is bold text\n")
italic("This is italic text\n")
underline("This is underlined text\n")
highlight("This is high lighted text\n")
crossout("This is crossed out text\n")
invisible("This is invisible text")
print("(Invisible Text)")