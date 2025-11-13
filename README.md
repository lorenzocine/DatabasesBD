# MotoGP Database Setup and Query Interface 🛵

Welcome to the MotoGP Database Setup and Query Interface! This is a brief guide that allows you to set up a MySQL database, populate tables with predefined data, and interact with it through a query interface based on riddles.

<br>



## Requirements 💻
- **Required Python Packages**:
  - `mysql-connector-python`
  - `pandas`
- **MySQL Database** installed and configured
- Data CSV files:
  - `rider table.csv`
  - `consolidated_race_table.csv`
  - `team table.csv`
  - `participates table.csv`
  - `ranking table.csv`

<br>

## Steps to a successful usage ✔
1. **Set file paths**: Replace `"path\to\file.csv"` with actual file paths
```python
def main():
    ...
    file paths = {
        "Rider": "path\to\rider table.csv",
        "Race": "path\consolidated_race_table .csv",
        "Team": "path\to\team table.csv",
        "Participates": "path\to\participates table.csv",
        "Ranking": "path\to\ranking table.csv"
    }
    ...
if __name__ == "__main__":
    main()
```
2. **Run the script**: start the program to enter your MySQL credentials when prompted.
3. **Solve the first riddle**: unlock the query interface by solving a fun riddle 🎭
4. **Choose a query**: select one of eight queries from the list displayed in the interface
5. **Solve another riddle**: Each query comes with its own riddle to solve before execution
6. **Enjoy the experience**: Dive into the data and enjoy the interactive challenge!😜

<br>

## IMPORTANT ⚠
Note that answers to all riddles are composed of lowercase single words (no articles). Be careful when writing answers as they are case sensitive. <br> <br> <br> <br> <br> 




## Closing Notes 🏁
Thank you for using the MotoGP Database Setup and Query Interface! If you have any feedback, feel free to reach out.

Developed with 🧠 by:
- Federico
- Francesco
- Lorenzo
- Sebastian Jr

Enjoy exploring the data! 🛵💨

