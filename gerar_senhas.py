from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Digite aqui exatamente o que você vai digitar na tela do login
print("NOVO CÓDIGO HELLEN:")
print(pwd_context.hash("146946"))

print("\nNOVO CÓDIGO TIAGO:")
print(pwd_context.hash("150588"))