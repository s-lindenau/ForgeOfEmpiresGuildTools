## Forge of Empires Guild Tools
Graphical tool for managing a guild in Forge of Empires by [slindenau](https://github.com/s-lindenau).  
This tool was originally inspired by [jjgomera/tesoreria_foe](https://github.com/jjgomera/tesoreria_foe). 

### Overview
All-in-one GUI overview to manage your guild and determine the least active members (to warn or kick)
* View guild members and their contributions
* View guild member activity in GE, GbG and Qi
* View guild treasury status and member donations

### Requirements
#### Functional
* Be a Leader of a guild in Forge of Empires
* Play with the [FoE-Tools](https://foe-tools.com/) browser extension (at least gather the data before starting a members analysis)
  * Visit the guilds members page for the data to be collected
  * Visit GE, GbG and Qi results at the end of a season for the activity data to be collected 
  * Visit individual guild members cities for their buildings data to be collected
  * Visit the guild treasury page for the donations data to be collected

#### Technical
* `python3 <https://www.python.org/>`, version 3.x required
* `pip <https://pypi.org/project/pip/>`, python package installer

### Dependencies
For installing the python dependencies this tool requires, run after downloading project:
* `pip install -r requirements.txt`

### Getting started
Download the files from the repository (ZIP, GitHub Desktop or `git clone`)  
Install the dependencies as mentioned above  
Run the file `tesorereria_foe.py`:
* `python tesorereria_foe.py`

### Downloading FoE-Tools data
To get the data of your guild members, you need to use the FoE-Tools browser extension.
* Play the game with the extension enabled
* Export the following files from the extension:
  * FoE-Tools: Settings -> Other -> Scroll down -> Import/Export -> Export -> Open tool -> (Select all) -> Export to ZIP
  * FoE: Global -> Guild -> Top left menu button -> Guild Contributions -> Browse all pages you want to analyze -> Export to CSV with FoE-Tools

### Screenshots

<img src="images/screenshots/screenshot.png" alt="screenshot of GUI"/>
