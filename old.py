import os
import pandas as pd
import matplotlib.pyplot as plt
from money_manager import MoneyManager

def main():
    files = [x for x in os.listdir() if ".xls" in x]
    
    mm = MoneyManager("yago")
    mm.add_data(files)
    mm.set_date(start_date="2023-01-01")
    print(mm.get_data())
    
    fig, axs = plt.subplots(1, 2)
    gastos_casa(mm.group_expenses(), axs[0])
    
    # grouped_unordered(mm.group_expenses(ignore_income=True), 
    #                   ["Other"], axs[0])
    # gastos_vs_ingresos(mm.get_data(), axs[1])
    plt.show()
    
def gastos_casa(data: dict, axes):
    final_data = {}
    sum_key = lambda dict_key: sum([x["amount"] for x in dict_key])
    
    comida = ["Lupa", "Mercadona", "McDonald", "Bazar", "Supermercado"]
    coche = ["Shell", "Easygas", "Telpark", "Parking", "Alisal", "E3055"]
    universidad = ["Matricula", "Ufg32-ciencias"]
    internet = ["Telefonica"]
    luz_gas = ["TotalEnergies"]     
    
    comida = {key: sum_key(data[key]) for key in comida}
    luz_gas = {key: sum_key(data[key]) for key in luz_gas}
    coche = {key: sum_key(data[key]) for key in coche}
    universidad = {key: sum_key(data[key]) for key in universidad}
    internet = {key: sum_key(data[key]) for key in internet}
    
    # Add to final data
    final_data["comida"] = sum(comida.values())
    final_data["internet"] = sum(internet.values())
    final_data["universidad"] = sum(universidad.values())
    final_data["coche"] = sum(coche.values())
    final_data["luz_gas"] = sum(luz_gas.values())
    
    total = sum([final_data[key] for key in final_data])
    
    for key in final_data:
        final_data[key] = final_data[key]/100
        print(f'{key.capitalize()}: {final_data[key]}€')
        
    print(f'\nTotal: {total/100}€')
    
    axes.barh(list(final_data.keys()), final_data.values())
    
    
def grouped_unordered(data: dict, exclude: list, axes):
    other = pd.DataFrame(data["Other"]).sort_values(by="amount")
    

    for key in data:
        data[key] = sum([x["amount"] for x in data[key]])/100
        
    for key in exclude:
        data.pop(key, None)
    
    # Remove empty elements
    data = {key: value for key, value in data.items() if value}
    axes.barh(list(data.keys()), data.values())

def gastos_vs_ingresos(data: pd.DataFrame, axes):
    pos = sum([i for i in data["amount"] if i > 0])
    neg = sum([i for i in data["amount"] if i < 0])
    total = pos - neg
    sizes = [abs(x/total) for x in [pos, neg]]
    
    # Plotting
    labels = "Ingresos", "Gastos"
    explode = (0, 0.1)
    axes.pie(sizes, labels=labels, explode=explode, shadow=True,
             autopct=lambda p: '{:.2f}€'.format(p * abs(total)/10000))
    
    
if __name__ == "__main__":
    main()