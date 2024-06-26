Some orienting instructions for logical people with python programming experience who aren't developers
 and/or may be new to the 'git this, pull that' and environment set-up experience in their toolkit yet

1. Open google.  If you can type a specific question, you will probably find a specific answer.
    If you don't know what you're looking for, follow instructions below and see what happens. Google your error messages 

2. Open a terminal window in your local environment.  I'm using an ubuntu 18.01 virtual machine managed
    by virtual box on my Lenovo window laptop.  Google 'how do I open my terminal window' if this is unclear.
    If you're using a Windows terminal, you may need to google 'how do I do $x' in windows where $x is any of
    the commands mentioned below.

3. Clone this repo (after googling and resolving 'apt-get install git' errors you encounter
                             - https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
```bash
mkdir NDA_submissions
cd NDA_submissions/
git init
git clone git@github.com:humanconnectome/NDA_submissions.git
```

4. Open [Intro to Behavioral Data Harmonization with the NDA for Redcap and Box users.pptx](./Intro%20to%20Behavioral%20Data%20Harmonization%20with%20the%20NDA%20for%20Redcap%20and%20Box%20users.pptx) in your new cloned folder for
    10 shareable slides of background and context for this repository (2 minute read).
 
5. rename the `dummycredentials` folder to `creds` and start populating the files therein
    with the authentication tokens/ids/keys you have at your disposal. BoxApp.json is for details pertaining to your BOX account
    secrets.yml is for any REDCap Databases.  Note that you may need to request permission for API access 
    from your database administrator before you even SEE the 'API playground' feature where you can generate tokens for
    your REDCap account.

```bash
mv dummycredentials/ creds/
emacs creds/secrets.yml &        # or open with any text editor you like to use...cool people use vim 
```

6. IMPORTANT PSA: Dont put your creds folder anywhere online ever.  You will face ethical dilemmas. You will get into trouble. 
    If you think you made a mistake, regenerate your tokens immediately, even if you're just working with a
    dummy test database so you know how to do this in case of a real emergency.  Remember that research data comes from real
    human beings who volunteered for Science under the condition that we will protect their PHI
    to the best of our ability.  The .gitignore file
    in this repo adds a layer of protection to ensure that the creds folder doesn't get pushed to the public facing
    part of this particular repo, but you actually NEED a creds folder locally to work with this repository.  The
    rest of the programs in this repo assume it exists and use the tokens etc
    therein so that you dont have to keep them in every program you write.  

7. Create a virtual python3 environment and install the libraries listed in the requirements.txt file
    Say what???? --> https://docs.python.org/3/tutorial/venv.html
```bash
python --version     # output says my default OS version is python 2.7.17 
python3 -m venv NDA_submissions_venv  #I changed directories and ran this command under  ~/.virtualenvs after following
                                         # instructions in error messages then changed back to NDA_submissions directory
source ~/.virtualenvs/NDA_submissions_venv/bin/activate  #now I'm in my 'activated' python3 virtual environment.
pip install -r requirements.txt --no-cache-dir  #--no-cache-dir is a bug workaround...might not be necessary
 ```

8. Install our library of REDCap and Box API (note you might need to turn off your VPN for this...no clue why,
    but it was messing with my own experiment from my socially distanced apartment).  Incidentally, we've had a number of
    curious VPN related issues with Jupyter notebooks that I'll just casually refer to here with no further explanation.  
```bash
pip install git+git://github.com/humanconnectome/ccf_libs@c11976646502966489ff7191ca0668cf618db6c7
# or try
pip install git+https://github.com/humanconnectome/ccf_libs --upgrade
```

9. Install the software that will allow you to load your 'NDA_submissions_venv' virtual environment into the jupyter notebooks
    written for the unique task of harmonizing data from REDCap and Box with structures at the NDA
```bash
pip install ipykernel
ipython kernel --user --name=NDA_submissions_venv jupyter-notebook
```

10. Launch notebook in terminal
```bash
jupyter notebook
```

should pop up a browser view of this directory, where you can open the Setup_Definitions.ipynb
    note that now your terminal window will be busy running the back end of this mini jupyter notebook web-server.
    Control C to exit out of the notebook back-end.

11. Open Setup_Definitions.ipynb (from the browser tool, not the terminal).  If you're not automatically prompted
     to accept the NDA_submissions_venv kernel, just find and switch to it from the kernel drop-down menu.  
     Select the first cell in the notebook and hit control+Enter.  If no errors, YAY! you are ready to begin the README.

12. If you swear you're making changes but nothing is changing, try shutting down the notebook (e.g control+c) and re launching.  Jupyter stores a lot of things in a
     memory cache somewhere that power users probably understand how to clear.  Let us know if you become one of these users so we can add your advice to this repo.  

    #better written source from which I'm borrowing concepts:
    https://github.com/GarageGames/Torque2D/wiki/Cloning-the-repo-and-working-with-Git

