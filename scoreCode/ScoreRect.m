
% pred is [x1 y1 x2 y2...] 
% true is [x1 y1; x2 y2; ...]
function score= ScoreRect(pred, true)


%pts 1 3 5 7 are x, 2 4 6 8 are y
    function a= area(pts)
        l1= sqrt((pts(1)-pts(3))^2 + (pts(2)-pts(4))^2);
        l2= sqrt((pts(5)-pts(3))^2 + (pts(6)-pts(4))^2);
        a= l1*l2;

    end

    % l1 is a pair of points, l2 is a pair of points
    % returns angle between the two lines, between 0 and pi
    function ang= angleDif(l1, l2)

        a1= atan2(l1(2,2)-l1(1,2),l1(2,1)-l1(1,1));
        a2= atan2(l2(2,2)-l2(1,2),l2(2,1)-l2(1,1));
        
        ang= abs(a1-a2);
        
    end



    % returns the area of a polygon without holes with vertices
    % given in order by list
    % list= [x1 y1; x2 y2; ....]
    function res= polyArea(list) 
                
        x= list(:,1);
        y= list(:,2);
        numVert= size(x,1);
        j = numVert;

        a=0;
        
        for i=1:numVert
            a = a+ ((x(j) + x(i))*(y(j) - y(i)));
            j = i;
        end
        res= abs(a * 0.5);
    end


    % e1, e2 are [x1 y1 x2 y2]
    % computes the intersection of 2 infinite lines defined by
    % points in e1 and e2
    function pt= ComputeIntersection(e1,e2)
       
        A1= e1(4)-e1(2);
        B1= e1(1)-e1(3);
        C1= A1*e1(1)+B1*e1(2);
       
        A2= e2(4)-e2(2);
        B2= e2(1)-e2(3);
        C2= A2*e2(1)+B2*e2(2);
        
        det= A1*B2- A2*B1;
        if det==0 % lines are parellel
            pt= e1(1:2);
        else
            x= (B2*C1-B1*C2)/det;
            y= (A1*C2-A2*C1)/det;
            pt= [x y];
        end
    end

    % Sutherland-Hodgman algorithm for polygon clipping
    % vertices in subj and clip must be given in counter clockwise order
    function poly= ClipPoly(subj, clip)
       
        j= size(clip,1);
        output= subj;
        for l=1:size(clip,1) % for each edge in clip
            edge= [clip(l,:) clip(j,:)];
          
            input= output; % input to next round is output of last round
            outInd= 1;
         	output= zeros(1,2);
            S= input(size(input,1),:);
            for k=1: size(input,1) % for each point in input
                E= input(k,:);
                tmpE= E-edge(1:2);
                cross1= cross([edge(3:4)-edge(1:2) 0], [tmpE 0]);
                tmpS= S-edge(1:2);
                cross2= cross([edge(3:4)-edge(1:2) 0],[tmpS 0]);
                if cross1(3)>0  % if E is inside edge
                    if cross2(3)<0
                        output(outInd,:)=(ComputeIntersection([S E],edge));
                        outInd= outInd+1;
                    end
                    output(outInd,:)=(E);
                    outInd= outInd+1;
               elseif cross2(3)>0
                    output(outInd,:)=(ComputeIntersection([S E],edge));
                    outInd= outInd+1;
               end
                S = E;
            end
            j=l;
        end
        poly= output;
    end
    

    % convert a 1d list of vertices to a 2d list of vertices
    function poly= lto2d(list)
        ind=1;
        for i=1:2:length(list)
            poly(ind,1)= list(i);
            poly(ind,2)= list(i+1);
            ind= ind+1;
        end
    end


    % plots a polygon with vertices given by pol
    function plotPoly(pol)
       
        plot(pol(:,1),pol(:,2),'m');
    end

    % Calculate the area of intersection of 2 rectangles r1, r2
    % whose vertices are given in counter-clockwise order
    function ar= intersectArea(r1, r2)
        pol=ClipPoly(r1,r2);   
        %plotPoly(pol);
        ar= polyArea(pol);
    end


    % Score the predicted rectangle
    pred1= lto2d(pred);
    %true1= lto2d(true);
    aDif=angleDif(pred1,true);
    if(aDif<pi/6||aDif>5*pi/6)
        score=intersectArea(pred1,true)/polyArea(pred1);
    else
        score=0;
    end
    
end