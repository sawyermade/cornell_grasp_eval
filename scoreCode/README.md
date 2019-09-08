To run the scorer, put ScoreAttempt.m and ScoreRect.m into the same
directory.

Edit the 5 fields at the top of ScoreAttempt.m
	dirTrue: set this to the directory which contains the true rectangles
	dirAttempt: set this to the directory containing the predicted
			rectangles
	prefix: set this to the prefix of the predicted rectangle files
			e.g. if your prediction for image pcd0000r.png is in
			pred0000.txt, prefix= 'pred';
	lo: the file number to start scoring from
	hi: the file number to stop scoring at
	
Then simply run ScoreAttempt.m