Webapp version of Jinglematic using Flask

A while back, I had a showerthought that basically all you needed to make a Christmas version of a song was to drop some sleighbells on the beat.  Since I'm in the process of learning python, I wondered if I could use that to get it done .  A few rabbit holes later, here we are.

The current iteration of the Jinglematic:

* does basic beat and tempo detection and adds jingle bells throughout, and on the upbeats if the song has a slower tempo.
* determines the key of the song, the relative major key (if necessary) and adds Christmas bells in the appropriate key
* calculates the average perceived loudness of the track and sets event levels accordingly
* detects up to two choruses and adds a magical sleighride effect.

Can be demoed at [rsmaldone.pythonanywhere.com](https://rsmaldone.pythonanywhere.com/).  Bear in mind that it's a long way to the North Pole, so it might take a minute or two for the elves to return your results.  The [locally-running version](https://github.com/RichardSmaldone/Jinglematic) is much faster.
