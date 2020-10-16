# Ecce-project_education
**IN THE PROCESS OF MIGRATING TO RASA 2.0**
This is an early stage MVP for a project to make building lessons using Rasa easy for non-technical educators. 

The premise is that conversational AI is a powerful tool for teaching. Particularly for those in rural India who have limited access to education, but have a smart phone and internet. 

The goal is to make this easy for any teacher to create lessons and add it to the regional version of the bot where users can speak to it in mixed language. 

Currently the lesson on fraction is based on [this Google Doc](https://docs.google.com/document/d/1LgeUIaqbyBnGFTDRHN3YF5hKgZFWIs5CE3sVX9yHKT0/edit?usp=sharing). Using this single lesson as a test case we are developing the right abstractions and syntax for teachers to be able to create simple lesson plans without worrying about the nuances and fail safe behaviors of a conversational AI assistants. 

TODOs for the MVP:
- [x] Connect to Rasa X with Integrated Version Control 
- [ ] Add WhatsApp as a channel 
- [ ] Lesson plan on fractions until wholes 
- [ ] Complete the happy path implementation of the fractions lessons
- [ ] Link bot to MySQL database:	
	- [ ] Extend Action Session Start to simulate SSO (Advanced Certification)
- [ ] Extend Rasa SDK to support automated question and validation where questions - and their specific information - is read from the MySQL database.  Done for:
	- [ ] Numerical Response Questions (NRQs)
	- [ ] Free Response Questions (FRQs)
	- [ ] Multiple Choice Questions (MCQs)

The Team:
- Arman Jindal
- Mahima Gupta 
- Dhruv Bhatia


In collaboration with [Ashwath Bharath - Teach For India](https://www.teachforindia.org/people/)
