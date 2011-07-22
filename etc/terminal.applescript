on run commande
tell application "Terminal"
activate
do script "clear ; " &commande&" ; exit"
end tell
end run