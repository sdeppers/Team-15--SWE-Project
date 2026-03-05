# INSTALLATION INSTRUCTIONS

1. Navigate to to **/bin/**.
2. Execute the installation script by typing **./install.bash** and press ENTER.

# USAGE

1. Navigate to **/bin/**.
2. Execute the main application by typing **./exec.bash** and press ENTER.
3. Left-click on the player ID field to manipulate\
the contents of that field using keyboard inputs, and press ENTER to finalize changes.
4. After a player ID is input, the 'Equipment ID' field is **automatically selected**,
and allows user to input an **INTEGER** value. Pressing ENTER assigns that\
'Equipment ID' to the selected player.
5. If a record for the stored player ID **does not exist in the database**, the 'codename'\
field for that player is **automatically selected**, after an Equipment ID is assigned\
to that player. If a player's player ID and Equipment ID fields are populated-\
**storing the player's codename by pressing ENTER will store that player in the database.**
6. If a record for the stored player ID **does exist in the database**\
that player's codename field is **automatically populated**.
7. The 'IP' and 'Port' fields may be selected by the user using mouse1 to store new\
information in, using the same method as storing information in the 'player ID' field.\
**NOTE:** An invalid IP or port number will result in termination of the application.
8. Press **F12** while in the 'player entry' screen to **remove all players** from the roster.
9. Press **F5** while in the 'player entry' screen to **enter the 'play action' screen.**\
**NOTE:** The only user input available from the 'play action' screen is **ESCAPE**.
10. Press **ESCAPE** at any time to **terminate** the application.
11. In the virtual machine's terminal, execute the command\
**psql -U student -d photon -c "Select * FROM players;"**\
to view the new contents of the database.

# CONTRIBUTORS

Name: Spencer Epperson---Github Alias: sdeppers\
Name: Gabriel McMillan-----Github Alias: paracetic\
Name: Saul Sanchez----------Github Alias: sauls8\
Name: Eshaan Thakore------Github Alias: eshaan-thakore\
Name: Elijah Wiggins---------Github Alias: elijwiggins