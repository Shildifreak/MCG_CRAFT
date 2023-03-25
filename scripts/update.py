import subprocess
import shutil


def update():
	print("Using git to update to newest version.")
	git = shutil.which("git")
	if git == None:
		print("No git installation found.")
		print("Please make sure git is installed and added to PATH.")
		return
	
	print("Checking current repository status.")
	command = [git,"status"]
	print("executing:"," ".join(command))
	p = subprocess.run(command, stdout=subprocess.DEVNULL)
	if p.returncode != 0:
		print("To use this update feature you will need a version of MCGCraft that was downloaded using the following command:")
		print("git clone https://github.com/Shildifreak/MCG_CRAFT.git")
		return
	
	print("Checking for updates and downloading them.")
	command = [git,"fetch"]
	print("executing:"," ".join(command))
	p = subprocess.run(command)
	if p.returncode != 0:
		print("Failed to download updates.")
		return
		
	print("Applying changes to local installation.")
	command = [git,"merge","--ff-only"]
	print("executing:"," ".join(command))
	p = subprocess.run(command)
	if p.returncode != 0:
		print("Pull with fast-forward merge failed.")
		print("This probably means you have made changes to game files,")
		print("and we have no way to know if they will be compatible with our update.")
		print("If you still want to update you will need to use git manually.")
		print("Add and commit local changes, then do a merge and see if the game still works.")
		return

	print("Success!")

update()
