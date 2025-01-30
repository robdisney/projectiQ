# projectiQ
coding project assistant

** Purpose ** 
Project IQ allows you to ask chatgpt for assistance with your coding project.  
It does this by collecting and sharing the entire contents of your project directory along with a directory tree as context for chatgpt, while filtering out items that you would prefer it not see or are too large and you want to keep your token usage down.  
** Required Libraries **

tkinter
openai

Workflow:

Change choose.py project_directory to your project directory.  the project directory should be within the directory that you are running these scripts from. 

For example, 

Root_dir 
- choose.py
- project.py
- project.txt
- openaicreds.py
  project_directory

Run "python3 choose.py" to run the choose function, which will bring up a tkinter app window displaying a tree of all files and folders in your project directory.  In the lower left-hand corner, it shows you the size of your project, in bytes.  As you select an item, it highlights the file or folder (and all its subcontents) and subtracts the total from the bytes count.  When you have selected files for exclusion, select "ok" at bottom right.  This will write an itemized list of excluded items to a file called "exclude.py".  Then put your prompt/question about your project in project.txt.  I often put things like whole traceback logs, error logs, etc in it as context for the problem i'm having.  Finally, run "python3 project.py"  This will send your prompt, the project directory tree, and the entire contents of your project directory to chatgpt for response.  
If you want to exclude more folders or files, you can run choose.py again and it will automatically populate the existing list of excluded files, which will show up in light blue in the tree.

