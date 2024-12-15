# STALKER: Monolith's Web Challenge

A FREE and OPEN SOURCE web-based CTF (Capture The Flag) challenge inspired by the S.T.A.L.K.E.R. game series atmosphere. This project is a fan creation and is not affiliated with or endorsed by GSC Game World or the official S.T.A.L.K.E.R. team.

## Description

Welcome to the Zone, stalker! This web challenge will test your hacking skills in a S.T.A.L.K.E.R.-themed environment. You were given a strange Monolith tablet, and now you have to trace down it's rising leader. Navigate through the mysterious Monolith's web presence and uncover its secrets.

## Installation

### Prerequisites
- Docker

### Quick Start
1. Clone the repository:
```bash
git clone https://github.com/Morronel/stalker-lab.git
cd stalker-lab
```

2. Build and run the container:
```bash
sudo docker build -t stalker-lab .
sudo docker run -p 0.0.0.0:5000:5000 stalker-lab
```

3. Access the challenge at:
```
http://127.0.0.1:5000
```

Flag is in stalker_ctf{FLAG} format. Good luck, stalker!

## License

This project is released under the MIT License. See the LICENSE file for details.

## Disclaimer

This is a fan-made CTF challenge inspired by the S.T.A.L.K.E.R. series. All S.T.A.L.K.E.R.-related trademarks and copyrights are property of their respective owners. This project is created for educational purposes only. 