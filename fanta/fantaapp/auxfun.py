def randomHash():
   N = 12
   return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(N))

