# Sacrament Coordination
This project tries to keep track of people who pass the sacrament on sundays. This includes information on the idividual who is passing the sacrement, and what week they are passing on.
In addition, this database also keeps track of if a person blessed or passed that week. 

<img src = ERD_Sacrament.png>


## Query I thought it did well on:
    Question: "Which members have passed sacrament on January 5th?"

    ```sql
    SELECT QM.Name
    FROM QuoremMembers QM
    JOIN Week W ON QM.MemberID = W.MemberID
    WHERE W.SundayDate = '2022-01-05' AND W.Role = 'Passer';
    ```

    **Answer**: No members have passed the sacrament on January 5th.

    This was a pretty simple query, and it did a great job at seeing that there were no passers on the fith. There were only people who blessed the sacrament.
    


## Question that it tripped up on
    Question: "List all members who are unavailable to serve."

    ```sql
    SELECT *
    FROM QuoremMembers
    WHERE TimesPassed > 3;
    ```

    **Answer**: Based on the provided SQL query results, there are no members who are unavailable to serve. All the members listed including John Doe, Ben Davis, Don Marks, and Matt Howels are available.


    To me, this question made no sense, but that was the point. I knew I had "Available", and "Unavailable" values in the database. I wanted to see if ChatGPT would take a guess and try to extrapilate a query based off of some of th values in SQL - regardless of their purpose. It didn't. I went in and looked at the actual response it gave back from this question, and it noticed this. So I consider that a point for Chat. The problem I have with this query is the fact that  this query (the incorrect query that it gave me) should have returned something. However, according to Chat, it didn't return anything. Which is just wrong. I tried to trip it up and it face-planted.


## Prompting Strategies I Used
    I tried to write some questions to each of the three categories covered in the article. Those can be found here:
        [My Eight Examples][my_eight_examples.txt]
    
    I found that when ChatGPT is asked something simple it does a pretty good job. However, it can struggle when data traverses over associations in the data and returns arbitrary data.

## Conclusion
    ChatGPT does pretty well in understanding SQL and interpreting it's outputs.