/*CREATE TABLE Flights(
	id SERIAL PRIMARY KEY,
	Origin TEXT NOT NULL,
	Destination TEXT NOT NULL,
	Duration INT NOT NULL
);*/

INSERT INTO Flights(Origin, Destination, Duration) VALUES('New York', 'London', 415)
INSERT INTO Flights(Origin, Destination, Duration) VALUES('Shanghai', 'Paris', 760)
INSERT INTO Flights(Origin, Destination, Duration) VALUES('Istanbul', 'Tokyo', 700)
INSERT INTO Flights(Origin, Destination, Duration) VALUES('New York', 'Paris', 435)
INSERT INTO Flights(Origin, Destination, Duration) VALUES('Moscow', 'Paris', 245)
INSERT INTO Flights(Origin, Destination, Duration) VALUES('Lima', 'New York', 455)

UPDATE Flights SET Duration = 430 WHERE Origin = 'New York' AND Destination = 'London'
SELECT * FROM Flights