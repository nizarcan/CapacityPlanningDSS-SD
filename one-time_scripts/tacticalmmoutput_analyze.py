import pandas as pd


def analyze_tkpm_results(file_dir):
    machine_legend = pd.read_excel(file_dir, sheet_name="machine_legend", index_col=0)
    total_overtime_results = pd.read_excel(file_dir, sheet_name="A")
    total_investment_results = pd.read_excel(file_dir, sheet_name="U")
    total_shift_results = pd.read_excel(file_dir, sheet_name="L")
    overtime_results = machine_legend
    investment_results = machine_legend
    shift_results = {x: machine_legend for x in range(1, 6)}

    total_overtime_results = total_overtime_results[total_overtime_results[total_overtime_results.columns[0]] == 2].iloc[:, 1:]
    for i in range(1, 6):
        temp_schedule = total_overtime_results[total_overtime_results[total_overtime_results.columns[1]] == i]
        temp_schedule.set_index(temp_schedule.columns[0], inplace=True)
        temp_schedule.drop(temp_schedule.columns[0], axis=1, inplace=True)
        temp_schedule = temp_schedule.sum(axis=1)
        overtime_results = pd.concat([overtime_results, pd.DataFrame(temp_schedule, columns=[i])], axis=1).fillna(0)

    overtime_results.sort_values(overtime_results.columns[0], inplace=True, ascending = True)
    overtime_results.columns = [""]+list(overtime_results.columns[1:])
    overtime_results.set_index(overtime_results.columns[0], inplace=True)

    for i in range(1, 6):
        temp_investment = total_investment_results[total_investment_results[total_investment_results.columns[1]] == i]
        temp_investment.set_index(temp_investment.columns[0], inplace=True)
        temp_investment.drop(temp_investment.columns[0], axis=1, inplace=True)
        temp_investment = temp_investment.sum(axis=1)
        investment_results = pd.concat([investment_results, pd.DataFrame(temp_investment, columns=[i])], axis=1).fillna(0)

    investment_results.sort_values(investment_results.columns[0], inplace=True, ascending = True)
    investment_results.columns = [""] + list(investment_results.columns[1:])
    investment_results.set_index(investment_results.columns[0], inplace=True)

    for i in range(1, 6):
        temp_shift = total_shift_results[total_shift_results[total_shift_results.columns[1]] == i]
        temp_shift.set_index(temp_shift.columns[0], inplace=True)
        temp_shift.drop(temp_shift.columns[0], axis=1, inplace=True)
        shift_results[i] = pd.concat([shift_results[i], temp_shift], axis=1).fillna(0)
        shift_results[i].sort_values(shift_results[i].columns[0], inplace = True, ascending = True)
        shift_results[i].columns = [""] + list(shift_results[i].columns[1:])
        shift_results[i].set_index(shift_results[i].columns[0], inplace = True)

    with pd.ExcelWriter("results.xlsx") as writer:
        overtime_results.to_excel(writer, sheet_name="overtime")
        investment_results.to_excel(writer, sheet_name="investment")
        for i in range(1, 6):
            shift_results[i].to_excel(writer, sheet_name="s"+str(i))


if __name__ == "__main__":
    tkpm_results = "D://Nizar//Downloads//TKPM_Results.xlsx"
    analyze_tkpm_results(tkpm_results)