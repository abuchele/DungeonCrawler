# Reflection and Synthesis
## Feedback and Decisions
The best information we got during this technical review was the feedback on our motion system. Playtesters (specifically Matt) noted that the movement was  
* too slow,
* did not render keys being held down properly,
* and did not always do what was expected.

We can incorporate this by tweaking the movement system to be more intuitive and smoother.

One of the other game groups also gave us some useful advice about pygame.clock, which could help us to manage the speed of our game if it becomes an issue. We will look into it and see how it can be implemented.

The other main piece of feedback we got was the general approval of our idea to use a guitar as a weapon, which will help us design dialogue and sprites moving forward.

Other than that, the feedback was generally positive, which means we are probably doing something right and will continue on our general trajectory.

## Review Process Reflection
The review itself went quite smoothly. There was a bit of difficulty playing on one computer that did not have scipy (that import was actually vestigial, so that error was a helpful reminder to delete it), but other than that, we were able to get it running on everyone's computer and watch their reactions to the game. It helped us to gague the speed of the game and how people in the game behave with relatively little effort on our part. It was also very flexible time-wise which made it easy to stay on schedule. It seems that playtesting once a game is mostly playable is, in fact, a viable technical review method.
