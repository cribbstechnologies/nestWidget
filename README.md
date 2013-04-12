This is a HTML/CSS/Python widget that uses the Nest API to get information from a thermostat and display the data in a read-only format. It leverages the nest.py script by Scott M Baker, smbaker@gmail.com, http://www.smbaker.com/ that's been modified quite a bit.

Installation instructions:
1. The nest.py script needs to be placed into a directory that is accessible via apache as a cgi script
2. Lines 39 and 40 in nest.py should be altered to use your Nest.com username and password so that the script can access your thermostat's information.
2. The GET URL on line 3 of jquery_nest.js needs to be modified to point at the publicly accessible location configured in step 1
3. The background image nestEmpty needs to be in the same directory as the jquery_nest.js file (or you can modify the location in line 4 of the file)
4. The HTML page where you'd like to inject the widget needs this markup wherever you want the widget: <div id="nestWidget"></div>

Example usage:
//This will load the information on page load and then create a timer to refresh the information every 10 seconds
$(document).ready(function() {
    $.nest($('#nestWidget'));
    window.setInterval(function(){$.nest($('#nestWidget'));}, 10000);
});