import backend.constants as constants
import pandas as pd
import numpy as np


def analyze_tkpm_results(file_dir, output_dir):
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

    with pd.ExcelWriter(output_dir) as writer:
        overtime_results.to_excel(writer, sheet_name="overtime")
        investment_results.to_excel(writer, sheet_name="investment")
        for i in range(1, 6):
            shift_results[i].to_excel(writer, sheet_name="s"+str(i))


def analyze_okpm_results(file_dir, output_dir):
    machine_legend = pd.read_excel(file_dir, sheet_name="machine_legend", index_col=0)
    results = pd.read_excel(file_dir, sheet_name="A")

    results = results[results[results.columns[0]] == 2].iloc[:, 1:]
    results.set_index(results.columns[0], inplace=True)
    results = pd.concat([machine_legend, results], axis=1).fillna(0)

    results.sort_values(results.columns[0], inplace=True, ascending = True)
    results.columns = [""]+list(results.columns[1:])
    results.set_index(results.columns[0], inplace=True)

    with pd.ExcelWriter(output_dir) as writer:
        results.to_excel(writer, sheet_name="overtime")


def analyze_okpb_results(file_dir, output_dir):
    current_part = ""
    tallies = pd.DataFrame(columns = ["Identifier", "Average", "Half Width", "Minimum", "Maximum", "Observations"])
    nq = pd.DataFrame(columns = ["Identifier", "Average", "Half Width", "Minimum", "Maximum", "Final Value"])
    nr = pd.DataFrame(columns = ["Identifier", "Average", "Half Width", "Minimum", "Maximum", "Final Value"])
    counters = pd.DataFrame(columns = ["Identifier", "Count", "Limit"])
    outputs = pd.DataFrame(columns = ["Identifier", "Value"])

    with open(file_dir, "r") as f:
        data = f.readlines()
        data = data[np.where(["Replication 1" in x for x in data])[0][0]:]
        data = data[np.where(["TALLY VARIABLES" in x for x in data])[0][0]:]
        data = data[:np.where(["Simulation run time" in x for x in data])[0][0]]
        for line in data:
            if ("____" in line) | (line == "\n") | ("Identifier" in line):
                continue
            if ("TALLY VARIABLES" in line) | ("DISCRETE-CHANGE VARIABLES" in line) | ("COUNTERS" in line) | (
                    "OUTPUTS" in line):
                current_part = line.strip()
                continue
            while "  " in line:
                line = line.replace("  ", " ")
            line = line.strip()
            line = line.split(" ")
            if current_part == "TALLY VARIABLES":
                tallies.loc[tallies.shape[0]] = line
            elif current_part == "DISCRETE-CHANGE VARIABLES":
                if "NQ" in line[0]:
                    line[0] = line[0].split("(")[1]
                    line[0] = line[0].split(")")[0]
                    nq.loc[nq.shape[0]] = line
                if "RESUTIL" in line[0]:
                    line[0] = line[0].split("(")[1]
                    line[0] = line[0].split(")")[0]
                    nr.loc[nr.shape[0]] = line
            elif current_part == "COUNTERS":
                counters.loc[counters.shape[0]] = line
            elif current_part == "OUTPUTS":
                outputs.loc[outputs.shape[0]] = line
        for df in [nq, nr]:
            df["Average"] = df["Average"].apply(lambda x: float(x))
            df.sort_values(by = "Average", ascending = False, inplace = True)
        with pd.ExcelWriter(output_dir) as writer:
            tallies.to_excel(writer, sheet_name = "tallies", index = False)
            nq.to_excel(writer, sheet_name = "nq", index = False)
            nr.to_excel(writer, sheet_name = "nr", index = False)
            counters.to_excel(writer, sheet_name = "counters", index = False)
            outputs.to_excel(writer, sheet_name = "outputs", index = False)


if __name__ == "__main__":
    analyze_tkpm_results(constants.results["TacticalMMInput"], constants.analysis["TKPM"])
    analyze_okpm_results(constants.results["OperationalMMInput"], constants.analysis["OKPM"])
    analyze_okpb_results(constants.results["OperationalSMInput"], constants.analysis["OKPB"])