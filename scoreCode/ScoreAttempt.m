
% Scores all attempts in dirAttempt by comparing the first rectangle
% in each attempt file with all known positive rectangles in the 
% corresponding file in dirTrue. The file numbering must be consistent

%%%%%%%%%% Change the paramters here %%%%%%%%%%

% The directory where the ground truth rectangles are located
dirTrue= 'Data/';
% The directory where the predicted rectangles are located
dirAttempt= 'Output/';
% The prefix of the predicted rectangle files
prefix= 'best_rectangles_'; 
% The range of attempted rectangles to score
lo=0;
hi=0;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% The predicted rectangles which did not match a true rectangle
fail= zeros(1,1);
% The predicted rectangles which did match a true rectangle
success= zeros(1,1);
% The number of predicted rectangles which matched a true rectangle
count=0;

ind=1;
sInd=1;

for j= lo:hi
    
    if j<10
        file= strcat('000',int2str(j));
    elseif j<100
        file= strcat('00',int2str(j));
    else
        file= strcat('0',int2str(j));
    end
    
    trueRects= load(strcat(dirTrue,'pcd', file,'cpos.txt'));
    attempt= load(strcat(dirAttempt,prefix,file,'.txt'));
    
    prevCount=count;
    if j==124
       r=1; 
    end
    for z=1:size(trueRects,1)/4
        if size(attempt,1)==0
            fail(ind)=j;
            ind= ind+1;
            break
        end
        val= ScoreRect(attempt(1,1:8),trueRects((z-1)*4+1:(z-1)*4+4,:));
        if(val>0.5)
            count= count+1;
            success(sInd)= j;
            sInd= sInd+1;
            break;
        end
    end
    if count==prevCount
        fail(ind)= j; % keeps track of failed test cases
        ind= ind+1;
    end
end
count
precision= count/(hi-lo+1)