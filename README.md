# Ecce-project_education

Can chat with MVB (Minimum Viable Bot) [here](http://35.232.27.88:8000/guest/conversations/production/78a995e30bd74272a9c393738d2af68b) as a guest tester. 


This is an early stageproject to make building and deploying lessons using Rasa easy for non-technical educators. 

The premise is that conversational AI is a powerful tool for teaching. Particularly for those in rural India who have limited access to education but have a smartphone and internet. It is a statement both about technology and pedagogy. EdTech today leads to passive students. Dialouge on the other hand engages and pushes students - no matter their economic or social circumstances - to engage with the material in front of them and learn. 

The goal is to make this easy for any teacher to create lessons and add it to the regional version of the bot where users can speak to it in mixed dialects. 

Currently the lesson on fraction is based on the doc the teams is working on in [this Google Doc](https://docs.google.com/document/d/1LgeUIaqbyBnGFTDRHN3YF5hKgZFWIs5CE3sVX9yHKT0/edit?usp=sharing). Using this single lesson as a test case we are developing the right abstractions and syntax for teachers to be able to create simple lesson plans without worrying about the nuances and fail safe behaviors of conversational AI assistants - so they can focus on what they do best: creativley and effectivley teaching the next generation (remotley for now!). 

TODOs for the MVP:
- [x] Completley migrate to Rasa 2.0 the fractions lessons
- [x] Deploy on Kubernetes cluster 
- [x] (Re) Connect to Rasa X with Integrated Version Control (when V 0.33 comes out) 
- [x] Add WhatsApp as a channel 
- [x] Lesson plan on fractions until wholes 
- [x] Complete the happy path implementation of the fractions lessons
- [ ] Link bot to PostgreSQL database:	
	- [ ] Extend Action Session Start to simulate SSO (Look at Advanced Certification code)
- [ ] Extend Rasa SDK to support automated question and validation where questions - and their specific information - is read from a custom DB for:
	- [ ] Numerical Response Questions (NRQs)
	- [ ] Free Response Questions (FRQs)
	- [ ] Multiple Choice Questions (MCQs)

The Team:
- Arman Jindal - arman.jindal@columbia.edu 
- Mahima Gupta - mahima_gupta@brown.edu
- Dhruv Bhatia - dhruv_bhatia@brown.edu 


In collaboration with [Ashwath Bharath - Teach For India](https://www.teachforindia.org/people/)
