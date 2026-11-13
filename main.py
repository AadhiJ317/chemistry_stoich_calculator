# imports
from bakery import assert_equal
from drafter import *
from dataclasses import dataclass


# site setup
set_website_title("Stoichiometry Calculator")
set_site_information(
    author="aadhij@udel.edu",
    description="A stoichiometry calculator that finds the limiting " +
                "reactant, yields, leftover masses, and heat of a reaction.",
    sources=["Chemistry 2e (OpenStax), Chapter 4"],
    planning=["design.pdf"],
    links=["VIDEO_LINK"]
)
hide_debug_information()
set_website_framed(False)


# dataclasses
@dataclass
class Compound:
    formula: str
    coefficient: int
    molar_mass: float
    mass: float
    remaining: float


@dataclass
class State:
    balanced_eq: str
    reactants: list[Compound]
    product: Compound
    lim_reagent: str
    yield_theory: float
    yield_percent: float
    enthalpy: float
    endothermic: bool
    heat_per_mole: float
    total_heat: float
    message: str


# helper functions
def new_state() -> State:
    """
    makes an empty State, used to start the site and to start over

    returns (State): a State with no equation, no reactants, a blank product,
        all numbers at 0, and no message
    """
    return State("", [], Compound("", 0, 0.0, 0.0, 0.0), "", 0.0, 0.0, 0.0,
                 False, 0.0, 0.0, "")


assert_equal(new_state(), State("", [], Compound("", 0, 0.0, 0.0, 0.0), "",
                                0.0, 0.0, 0.0, False, 0.0, 0.0, ""))
assert_equal(new_state().reactants, [])
assert_equal(new_state().product, Compound("", 0, 0.0, 0.0, 0.0))


def example_state() -> State:
    """
    makes a filled-in State for N2 + 3H2 -> 2NH3, only used in unit tests

    returns (State): a State with 28 g N2, 4 g H2, 20 g of NH3 made,
        and a heat of reaction of -92 kJ
    """
    reactants = [Compound("N2", 1, 28.0, 28.0, 0.0),
                 Compound("H2", 3, 2.0, 4.0, 0.0)]
    product = Compound("NH3", 2, 17.0, 20.0, 0.0)
    return State("N2 + 3H2 -> 2NH3", reactants, product, "", 0.0, 0.0, -92.0,
                 False, 0.0, 0.0, "")


assert_equal(example_state().reactants,
             [Compound("N2", 1, 28.0, 28.0, 0.0),
              Compound("H2", 3, 2.0, 4.0, 0.0)])
assert_equal(example_state().product, Compound("NH3", 2, 17.0, 20.0, 0.0))
assert_equal(example_state().enthalpy, -92.0)


def is_signed_number(text: str) -> bool:
    """
    checks if text from a text box is any number, including negatives,
        like "-92" or "4.5", by going through it one character at a time

    args: text(str): the text from a text box

    returns (bool): True if the text has only digits, at most one dot,
        and at most one minus sign at the very start
    """
    dots = 0
    digits = 0
    position = 0
    for char in text:
        if char == ".":
            dots = dots + 1
        elif char in "0123456789":
            digits = digits + 1
        elif char != "-" or position > 0:
            return False
        position = position + 1
    return (dots <= 1 and digits > 0)


assert_equal(is_signed_number("-92.5"), True)
assert_equal(is_signed_number("1.2.3"), False)
assert_equal(is_signed_number("5-"), False)


def is_number(text: str) -> bool:
    """
    checks if text from a text box is a number above 0, like "5" or "2.5"

    args: text(str): the text from a text box

    returns (bool): True if the text is a number above 0, False otherwise
    """
    if is_signed_number(text):
        return (float(text) > 0)
    else:
        return False


assert_equal(is_number("2.5"), True)
assert_equal(is_number("0"), False)
assert_equal(is_number("-3"), False)


def check_compound(formula: str, coefficient: str, molar_mass: str,
                   mass: str) -> str:
    """
    checks the text box inputs for one compound and makes an error message
        for the first one that is wrong

    args: formula(str): the chemical formula
          coefficient(str): the coefficient from the balanced equation
          molar_mass(str): the molar mass in g/mol
          mass(str): the mass in grams

    returns (str): the error message, or "" if every input is valid
    """
    if formula == "":
        return "Enter a formula."
    elif not is_number(coefficient) or "." in coefficient:
        return "Coefficient must be a whole number above 0."
    elif not is_number(molar_mass):
        return "Molar mass must be a number above 0."
    elif not is_number(mass):
        return "Mass must be a number above 0."
    else:
        return ""


assert_equal(check_compound("H2", "3", "2.016", "4.5"), "")
assert_equal(check_compound("H2", "0", "2.016", "4"),
             "Coefficient must be a whole number above 0.")
assert_equal(check_compound("H2", "3", "abc", "4"),
             "Molar mass must be a number above 0.")


def make_compound(formula: str, coefficient: str, molar_mass: str,
                  mass: str) -> Compound:
    """
    turns the text box inputs for one compound into a Compound

    args: formula(str): the chemical formula
          coefficient(str): the coefficient from the balanced equation
          molar_mass(str): the molar mass in g/mol
          mass(str): the mass in grams

    returns (Compound): the new Compound, with remaining set to 0.0
    """
    return Compound(formula, int(coefficient), float(molar_mass),
                    float(mass), 0.0)


assert_equal(make_compound("H2O", "2", "18", "36"),
             Compound("H2O", 2, 18.0, 36.0, 0.0))
assert_equal(make_compound("H2", "3", "2.016", "4").molar_mass, 2.016)
assert_equal(make_compound("O2", "1", "32", "36.5").mass, 36.5)


def reaction_amount(compound: Compound) -> float:
    """
    finds a compound's moles divided by its coefficient, which is how many
        times the reaction can run with that compound

    args: compound(Compound): the compound to check

    returns (float): (mass / molar mass) / coefficient
    """
    return ((compound.mass / compound.molar_mass) / compound.coefficient)


assert_equal(reaction_amount(Compound("N2", 1, 28.0, 28.0, 0.0)), 1.0)
assert_equal(reaction_amount(Compound("H2", 3, 2.0, 6.0, 0.0)), 1.0)
assert_equal(reaction_amount(Compound("O2", 2, 32.0, 16.0, 0.0)), 0.25)


def find_limiting(reactants: list[Compound]) -> Compound:
    """
    finds the limiting reactant, the one with the smallest reaction amount,
        since it runs out first

    args: reactants(list[Compound]): all the reactants

    returns (Compound): the limiting reactant
    """
    limiting = reactants[0]
    for reactant in reactants:
        if reaction_amount(reactant) < reaction_amount(limiting):
            limiting = reactant
    return limiting


assert_equal(find_limiting(example_state().reactants).formula, "H2")
assert_equal(find_limiting([Compound("O2", 1, 32.0, 16.0, 0.0),
                            Compound("H2", 2, 2.0, 4.0, 0.0)]).formula, "O2")
assert_equal(find_limiting([Compound("O2", 1, 32.0, 16.0, 0.0)]).formula,
             "O2")


def set_leftovers(reactants: list[Compound],
                  amount: float) -> list[Compound]:
    """
    finds how many grams of each reactant are left after the reaction and
        saves it in that reactant's remaining field

    args: reactants(list[Compound]): all the reactants
          amount(float): the limiting reactant's reaction amount

    returns (list[Compound]): the same reactants, with remaining filled in
    """
    for reactant in reactants:
        used = ((amount * reactant.coefficient) * reactant.molar_mass)
        reactant.remaining = (reactant.mass - used)
        if reactant.remaining < 0:
            reactant.remaining = 0.0
    return reactants


assert_equal(round(set_leftovers(example_state().reactants, 2 / 3)[0]
                   .remaining, 2), 9.33)
assert_equal(round(set_leftovers(example_state().reactants, 2 / 3)[1]
                   .remaining, 2), 0.0)
assert_equal(set_leftovers([Compound("H2", 3, 2.0, 4.0, 0.0)], 1.0)[0]
             .remaining, 0.0)


def reactant_lines(reactants: list[Compound]) -> list[str]:
    """
    makes one line of text for each reactant added so far, shown on the
        reactants page

    args: reactants(list[Compound]): all the reactants

    returns (list[str]): lines like "3 H2: 4.0 g"
    """
    lines = []
    for reactant in reactants:
        lines.append(str(reactant.coefficient) + " " + reactant.formula +
                     ": " + str(reactant.mass) + " g")
    return lines


assert_equal(reactant_lines(example_state().reactants),
             ["1 N2: 28.0 g", "3 H2: 4.0 g"])
assert_equal(reactant_lines([Compound("O2", 1, 32.0, 2.5, 0.0)]),
             ["1 O2: 2.5 g"])
assert_equal(reactant_lines([]), [])


def result_lines(reactants: list[Compound]) -> list[str]:
    """
    makes one line of text for each reactant with its starting moles and
        leftover grams, shown on the results page

    args: reactants(list[Compound]): all the reactants

    returns (list[str]): lines like "N2: 1.0 mol at start, 9.33 g left over"
    """
    lines = []
    for reactant in reactants:
        moles = round((reactant.mass / reactant.molar_mass), 2)
        left = round(reactant.remaining, 2)
        lines.append(reactant.formula + ": " + str(moles) +
                     " mol at start, " + str(left) + " g left over")
    return lines


assert_equal(result_lines([Compound("N2", 1, 28.0, 28.0, 9.333),
                           Compound("H2", 3, 2.0, 4.0, 0.0)]),
             ["N2: 1.0 mol at start, 9.33 g left over",
              "H2: 2.0 mol at start, 0.0 g left over"])
assert_equal(result_lines([Compound("O2", 1, 32.0, 10.0, 3.14159)]),
             ["O2: 0.31 mol at start, 3.14 g left over"])
assert_equal(result_lines([]), [])


def heat_type(endothermic: bool) -> str:
    """
    makes the sentence saying if the reaction absorbs or releases heat

    args: endothermic(bool): whether the reaction is endothermic

    returns (str): the endothermic or exothermic sentence
    """
    if endothermic:
        return "Endothermic: the reaction absorbs heat."
    else:
        return "Exothermic: the reaction releases heat."


assert_equal(heat_type(True), "Endothermic: the reaction absorbs heat.")
assert_equal(heat_type(False), "Exothermic: the reaction releases heat.")


def solve(state: State) -> State:
    """
    finds every result: the limiting reactant, leftovers, theoretical and
        percent yield, endothermic or exothermic, heat per mole, and the
        heat for the amounts entered

    args: state(State): a State with reactants, a product, and enthalpy

    returns (State): the same State with every result filled in, plus a
        warning message if percent yield is over 100
    """
    limiting = find_limiting(state.reactants)
    amount = reaction_amount(limiting)
    state.lim_reagent = limiting.formula
    set_leftovers(state.reactants, amount)
    state.yield_theory = ((amount * state.product.coefficient) *
                          state.product.molar_mass)
    state.yield_percent = ((state.product.mass / state.yield_theory) * 100)
    state.endothermic = (state.enthalpy > 0)
    state.heat_per_mole = (state.enthalpy / state.product.coefficient)
    state.total_heat = (state.enthalpy * amount)
    if state.yield_percent > 100:
        state.message = ("Warning: percent yield is over 100%. " +
                         "Check your masses.")
    return state


assert_equal(solve(example_state()).lim_reagent, "H2")
assert_equal(round(solve(example_state()).total_heat, 2), -61.33)
assert_equal(solve(State("", [Compound("H2", 3, 2.0, 4.0, 0.0)],
                         Compound("NH3", 2, 17.0, 30.0, 0.0), "", 0.0, 0.0,
                         92.0, False, 0.0, 0.0, "")).message,
             "Warning: percent yield is over 100%. Check your masses.")


# routes
@route
def index(state: State) -> Page:
    """
    shows the start page with a box for the balanced equation

    args: state(State): the site's state

    returns (Page): the start page
    """
    return Page(state, [
        Header("Stoichiometry Calculator"),
        "Finds the limiting reactant, yields, and heat of a reaction.",
        LineBreak(),
        "Balanced equation (example: N2 + 3H2 -> 2NH3):",
        TextBox("equation", state.balanced_eq),
        LineBreak(),
        Button("Start", "save_equation")
    ])


assert_equal(index(new_state()), Page(new_state(), [
    Header("Stoichiometry Calculator"),
    "Finds the limiting reactant, yields, and heat of a reaction.",
    LineBreak(),
    "Balanced equation (example: N2 + 3H2 -> 2NH3):",
    TextBox("equation", ""),
    LineBreak(),
    Button("Start", "save_equation")
]))
assert_equal(index(example_state()), Page(example_state(), [
    Header("Stoichiometry Calculator"),
    "Finds the limiting reactant, yields, and heat of a reaction.",
    LineBreak(),
    "Balanced equation (example: N2 + 3H2 -> 2NH3):",
    TextBox("equation", "N2 + 3H2 -> 2NH3"),
    LineBreak(),
    Button("Start", "save_equation")
]))


@route
def reactants_page(state: State) -> Page:
    """
    shows the page for adding reactants one at a time, with a Done button
        once at least one reactant is added

    args: state(State): the site's state

    returns (Page): the reactants page
    """
    content = [
        Header("Reactants"),
        state.message, LineBreak(),
        "Formula:", TextBox("formula"), LineBreak(),
        "Coefficient:", TextBox("coefficient"), LineBreak(),
        "Molar mass (g/mol):", TextBox("molar_mass"), LineBreak(),
        "Mass (g):", TextBox("mass"), LineBreak(),
        Button("Add reactant", "add_reactant"), LineBreak(),
        "Reactants so far:",
        BulletedList(reactant_lines(state.reactants))
    ]
    if len(state.reactants) > 0:
        content.append(Button("Done", "done"))
    return Page(state, content)


assert_equal(reactants_page(new_state()), Page(new_state(), [
    Header("Reactants"),
    "", LineBreak(),
    "Formula:", TextBox("formula"), LineBreak(),
    "Coefficient:", TextBox("coefficient"), LineBreak(),
    "Molar mass (g/mol):", TextBox("molar_mass"), LineBreak(),
    "Mass (g):", TextBox("mass"), LineBreak(),
    Button("Add reactant", "add_reactant"), LineBreak(),
    "Reactants so far:",
    BulletedList([])
]))
assert_equal(reactants_page(example_state()), Page(example_state(), [
    Header("Reactants"),
    "", LineBreak(),
    "Formula:", TextBox("formula"), LineBreak(),
    "Coefficient:", TextBox("coefficient"), LineBreak(),
    "Molar mass (g/mol):", TextBox("molar_mass"), LineBreak(),
    "Mass (g):", TextBox("mass"), LineBreak(),
    Button("Add reactant", "add_reactant"), LineBreak(),
    "Reactants so far:",
    BulletedList(["1 N2: 28.0 g", "3 H2: 4.0 g"]),
    Button("Done", "done")
]))
assert_equal(reactants_page(State("", [], Compound("", 0, 0.0, 0.0, 0.0), "",
                                  0.0, 0.0, 0.0, False, 0.0, 0.0,
                                  "Mass must be a number above 0."))
             .content[1], "Mass must be a number above 0.")


@route
def product_page(state: State) -> Page:
    """
    shows the page for entering the product and the heat of reaction

    args: state(State): the site's state

    returns (Page): the product page
    """
    return Page(state, [
        Header("Product"),
        state.message, LineBreak(),
        "Formula:", TextBox("formula"), LineBreak(),
        "Coefficient:", TextBox("coefficient"), LineBreak(),
        "Molar mass (g/mol):", TextBox("molar_mass"), LineBreak(),
        "Actual mass made (g):", TextBox("mass"), LineBreak(),
        "Heat of reaction, ΔH (kJ):", TextBox("enthalpy"), LineBreak(),
        Button("Calculate", "calculate"),
        Button("Back", "reactants_page")
    ])


assert_equal(product_page(example_state()), Page(example_state(), [
    Header("Product"),
    "", LineBreak(),
    "Formula:", TextBox("formula"), LineBreak(),
    "Coefficient:", TextBox("coefficient"), LineBreak(),
    "Molar mass (g/mol):", TextBox("molar_mass"), LineBreak(),
    "Actual mass made (g):", TextBox("mass"), LineBreak(),
    "Heat of reaction, ΔH (kJ):", TextBox("enthalpy"), LineBreak(),
    Button("Calculate", "calculate"),
    Button("Back", "reactants_page")
]))
assert_equal(product_page(State("", [], Compound("", 0, 0.0, 0.0, 0.0), "",
                                0.0, 0.0, 0.0, False, 0.0, 0.0,
                                "ΔH must be a number.")).content[1],
             "ΔH must be a number.")
assert_equal(product_page(new_state()).state, new_state())


@route
def results_page(state: State) -> Page:
    """
    shows the limiting reactant, yields, leftovers, and heat info

    args: state(State): the site's state, after solve has filled it in

    returns (Page): the results page
    """
    product = state.product
    return Page(state, [
        Header("Results"),
        state.message, LineBreak(),
        "Equation: " + state.balanced_eq, LineBreak(),
        "Limiting reactant: " + state.lim_reagent, LineBreak(),
        "Theoretical yield of " + product.formula + ": " +
        str(round(state.yield_theory, 2)) + " g", LineBreak(),
        "Actual yield: " + str(product.mass) + " g", LineBreak(),
        "Percent yield: " + str(round(state.yield_percent, 2)) + "%",
        LineBreak(),
        "Reactants:",
        BulletedList(result_lines(state.reactants)),
        heat_type(state.endothermic), LineBreak(),
        "Heat per mole of " + product.formula + ": " +
        str(round(state.heat_per_mole, 2)) + " kJ/mol", LineBreak(),
        "Heat for these amounts: " + str(round(state.total_heat, 2)) +
        " kJ", LineBreak(),
        Button("Enthalpy info", "enthalpy_page"),
        Button("Start over", "start_over")
    ])


assert_equal(results_page(solve(example_state())),
             Page(solve(example_state()), [
                 Header("Results"),
                 "", LineBreak(),
                 "Equation: N2 + 3H2 -> 2NH3", LineBreak(),
                 "Limiting reactant: H2", LineBreak(),
                 "Theoretical yield of NH3: 22.67 g", LineBreak(),
                 "Actual yield: 20.0 g", LineBreak(),
                 "Percent yield: 88.24%", LineBreak(),
                 "Reactants:",
                 BulletedList(["N2: 1.0 mol at start, 9.33 g left over",
                               "H2: 2.0 mol at start, 0.0 g left over"]),
                 "Exothermic: the reaction releases heat.", LineBreak(),
                 "Heat per mole of NH3: -46.0 kJ/mol", LineBreak(),
                 "Heat for these amounts: -61.33 kJ", LineBreak(),
                 Button("Enthalpy info", "enthalpy_page"),
                 Button("Start over", "start_over")
             ]))
assert_equal(results_page(solve(State("", [Compound("H2", 3, 2.0, 4.0, 0.0)],
                                      Compound("NH3", 2, 17.0, 30.0, 0.0),
                                      "", 0.0, 0.0, 92.0, False, 0.0, 0.0, "")))
             .content[1],
             "Warning: percent yield is over 100%. Check your masses.")
assert_equal(results_page(solve(State("", [Compound("H2", 3, 2.0, 4.0, 0.0)],
                                      Compound("NH3", 2, 17.0, 30.0, 0.0),
                                      "", 0.0, 0.0, 92.0, False, 0.0, 0.0, "")))
             .content[15], "Endothermic: the reaction absorbs heat.")


@route
def enthalpy_page(state: State) -> Page:
    """
    explains what the sign of the heat of reaction means and shows how
        heat per mole and the heat for these amounts were found

    args: state(State): the site's state, after solve has filled it in

    returns (Page): the enthalpy page
    """
    product = state.product
    return Page(state, [
        Header("Enthalpy"),
        "ΔH of the reaction: " + str(state.enthalpy) + " kJ", LineBreak(),
        heat_type(state.endothermic), LineBreak(),
        "A negative ΔH means the reaction releases heat (exothermic).",
        LineBreak(),
        "A positive ΔH means the reaction absorbs heat (endothermic).",
        LineBreak(),
        "Heat per mole of " + product.formula + " = ΔH / coefficient = " +
        str(state.enthalpy) + " / " + str(product.coefficient) + " = " +
        str(round(state.heat_per_mole, 2)) + " kJ/mol", LineBreak(),
        "Heat for these amounts = ΔH x (limiting moles / coefficient) = " +
        str(round(state.total_heat, 2)) + " kJ", LineBreak(),
        Button("Back", "results_page")
    ])


assert_equal(enthalpy_page(solve(example_state())),
             Page(solve(example_state()), [
                 Header("Enthalpy"),
                 "ΔH of the reaction: -92.0 kJ", LineBreak(),
                 "Exothermic: the reaction releases heat.", LineBreak(),
                 "A negative ΔH means the reaction releases heat " +
                 "(exothermic).",
                 LineBreak(),
                 "A positive ΔH means the reaction absorbs heat " +
                 "(endothermic).",
                 LineBreak(),
                 "Heat per mole of NH3 = ΔH / coefficient = -92.0 / 2 = " +
                 "-46.0 kJ/mol", LineBreak(),
                 "Heat for these amounts = ΔH x (limiting moles / " +
                 "coefficient) = -61.33 kJ", LineBreak(),
                 Button("Back", "results_page")
             ]))
assert_equal(enthalpy_page(solve(State("", [Compound("H2", 3, 2.0, 4.0, 0.0)],
                                       Compound("NH3", 2, 17.0, 30.0, 0.0),
                                       "", 0.0, 0.0, 92.0, False, 0.0,
                                       0.0, "")))
             .content[3], "Endothermic: the reaction absorbs heat.")
assert_equal(enthalpy_page(solve(State("", [Compound("H2", 3, 2.0, 4.0, 0.0)],
                                       Compound("NH3", 2, 17.0, 30.0, 0.0),
                                       "", 0.0, 0.0, 92.0, False, 0.0,
                                       0.0, "")))
             .content[9],
             "Heat per mole of NH3 = ΔH / coefficient = 92.0 / 2 = " +
             "46.0 kJ/mol")


@route
def save_equation(state: State, equation: str) -> Page:
    """
    saves the balanced equation from the start page and goes to the
        reactants page

    args: state(State): the site's state
          equation(str): the balanced equation from the text box

    returns (Page): the reactants page
    """
    state.balanced_eq = equation
    state.message = ""
    return reactants_page(state)


assert_equal(save_equation(new_state(), "N2 + 3H2 -> 2NH3").state.balanced_eq,
             "N2 + 3H2 -> 2NH3")
assert_equal(save_equation(new_state(), "N2 + 3H2 -> 2NH3").content[0],
             Header("Reactants"))
assert_equal(save_equation(State("", [], Compound("", 0, 0.0, 0.0, 0.0), "",
                                 0.0, 0.0, 0.0, False, 0.0, 0.0, "old error"),
                           "").state.message, "")


@route
def add_reactant(state: State, formula: str, coefficient: str,
                 molar_mass: str, mass: str) -> Page:
    """
    adds a reactant to the list if its inputs are valid, or shows an error
        message if one is wrong

    args: state(State): the site's state
          formula(str): the reactant's formula
          coefficient(str): the reactant's coefficient
          molar_mass(str): the reactant's molar mass in g/mol
          mass(str): the reactant's starting mass in grams

    returns (Page): the reactants page
    """
    state.message = check_compound(formula, coefficient, molar_mass, mass)
    if state.message == "":
        state.reactants.append(make_compound(formula, coefficient,
                                             molar_mass, mass))
    return reactants_page(state)


assert_equal(len(add_reactant(example_state(), "O2", "1", "32", "32")
                 .state.reactants), 3)
assert_equal(add_reactant(new_state(), "H2", "3", "2", "abc").state.message,
             "Mass must be a number above 0.")
assert_equal(add_reactant(example_state(), "", "1", "2", "4").state.reactants,
             example_state().reactants)


@route
def done(state: State) -> Page:
    """
    clears any old error message and goes to the product page

    args: state(State): the site's state

    returns (Page): the product page
    """
    state.message = ""
    return product_page(state)


assert_equal(done(example_state()), product_page(example_state()))
assert_equal(done(State("", [], Compound("", 0, 0.0, 0.0, 0.0), "", 0.0, 0.0,
                        0.0, False, 0.0, 0.0, "old error")).state.message, "")
assert_equal(done(example_state()).state.reactants, example_state().reactants)


@route
def calculate(state: State, formula: str, coefficient: str, molar_mass: str,
              mass: str, enthalpy: str) -> Page:
    """
    saves the product and heat of reaction, then finds every result

    args: state(State): the site's state
          formula(str): the product's formula
          coefficient(str): the product's coefficient
          molar_mass(str): the product's molar mass in g/mol
          mass(str): the actual mass of product made in grams
          enthalpy(str): the heat of reaction in kJ

    returns (Page): the results page, or the product page with an error
        message if an input is wrong
    """
    state.message = check_compound(formula, coefficient, molar_mass, mass)
    if state.message == "" and not is_signed_number(enthalpy):
        state.message = "ΔH must be a number."
    if state.message != "":
        return product_page(state)
    state.product = make_compound(formula, coefficient, molar_mass, mass)
    state.enthalpy = float(enthalpy)
    return results_page(solve(state))


assert_equal(calculate(example_state(), "NH3", "2", "17", "20", "-92")
             .content[5], "Limiting reactant: H2")
assert_equal(calculate(example_state(), "NH3", "2", "17", "20", "92")
             .state.endothermic, True)
assert_equal(calculate(example_state(), "NH3", "2", "17", "20", "abc")
             .content[1], "ΔH must be a number.")


@route
def start_over(state: State) -> Page:
    """
    throws away the old State and goes back to the start page

    args: state(State): the site's state

    returns (Page): the start page with an empty State
    """
    return index(new_state())


assert_equal(start_over(solve(example_state())), index(new_state()))
assert_equal(start_over(example_state()).state.reactants, [])
assert_equal(start_over(new_state()), index(new_state()))


# start
start_server(new_state())
