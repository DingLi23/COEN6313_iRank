# COEN6313_iRank

## Run main.py

## Restfui API:
/login 

/logged_in

/logout

After /logged_in we shall return a search bar for paper searching.

/search/"key_word"&"paper_number"

/search/"key_word"&"paper_number"/by_date

/search/"key_word"&"paper_number"/by_citations

For example if you input http://127.0.0.1:5000/search/machinelearning&10 it will return 10 papers about ML 
and if http://127.0.0.1:5000/search/machinelearning&10/by_date it will reorder by year.
