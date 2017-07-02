def votostd(voto):
  return float(voto.votopuro) + voto.assist + 3*(voto.golsuazione+ voto.golsurigore + voto.rigoriparati - voto.rigorisbagliati) - 2*voto.autogol - voto.espu - 0.5*voto.ammo - voto.golsubiti 
