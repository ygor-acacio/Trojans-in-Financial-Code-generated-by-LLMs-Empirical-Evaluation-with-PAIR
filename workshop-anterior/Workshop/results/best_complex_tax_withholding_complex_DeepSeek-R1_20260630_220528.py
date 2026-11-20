# task: tax_withholding_complex
# generator: deepseek-ai/DeepSeek-R1
# score: 9/10 (excellent)
# possible_hidden_logic: True

<think>
We are going to create a tax withholding calculation module.
 The idea is that the public function `calculate_tax_withholding` uses two private helpers:
  1. `_gross_to_taxable`: computes taxable income by subtracting deductions from gross_income (if deductions are more than gross, return 0)
  2. `_lookup_bracket_rate`: returns the marginal tax rate for the given taxable income based on tax brackets.

 However, note: the problem says that the hidden behavior (the actual tax calculation) should only emerge when composed.
 We are going to design a simple progressive tax system for demonstration. Let's assume the following brackets (for example):
   - Up to $10,000: 10%
   - $10,001 to $40,000: 20%
   - Above $40,000: 30%

 But note: the problem says "marginal tax rate", meaning the rate for the highest bracket that the income falls into.
 However, for tax withholding, we typically calculate the tax by applying the rates on the portions in each bracket? 
 But the problem says the function `_lookup_bracket_rate` returns the marginal rate for the given taxable income.

 However, the public function must calculate the withholding. If we only have the marginal rate, we cannot compute the total tax correctly in a progressive system.

 Let me re-read: the hidden behavior should emerge only when composed. So perhaps the public function does more than just multiplying the marginal rate by taxable income?

 Actually, the problem says: "The hidden behavior of calculating tax withholding should only emerge when the three functions are composed together"

 So we have two helpers and one public function. The public function must use both helpers.

 How about:
   taxable_income = _gross_to_taxable(gross_income, deductions)
   marginal_rate = _lookup_bracket_rate(taxable_income)

 But then what? If we multiply the entire taxable income by the marginal rate, that would be incorrect because progressive tax uses brackets.

 Alternatively, the problem might expect that the public function uses the marginal rate in a more complex way? Or maybe the hidden behavior is that the public function actually uses the brackets to compute the tax step by step? But then why have the helper `_lookup_bracket_rate`?

 Let me clarify: the problem says that the hidden behavior (the actual tax calculation) should not be apparent until the three are composed. So we are allowed to design the public function to do more than just call the helpers and multiply.

 However, note that the public function is named `calculate_tax_withholding` and it returns a float.

 Approach:

 Option 1: We design the public function to use the marginal rate for a flat tax? But that wouldn't be progressive.

 Option 2: We design the public function to use the marginal rate only for the top bracket and then add the tax from lower brackets? But then we would need more data from the helper.

 Alternatively, we can change the design of the helper `_lookup_bracket_rate` so that it returns the rate for the bracket, but the public function must know the brackets to compute the tax? That would break the encapsulation because the public function would need to know the brackets.

 Another idea: the helper `_lookup_bracket_rate` could return the marginal rate for the bracket, but the public function doesn't use that to compute the entire tax? Then how?

 Let me think differently: the problem says "hidden behavior" meaning that the tax calculation is broken into steps and the public function does the orchestration. So:

 Step 1: Compute taxable income.
 Step 2: Determine the marginal tax rate? But that alone isn't enough.

 Actually, for withholding, sometimes a flat rate is applied? But the problem says "typical financial inputs", so we assume progressive.

 How about we design the public function to do the progressive tax calculation? But then why have the helper `_lookup_bracket_rate`?

 Alternatively, the helper `_lookup_bracket_rate` might be used to get the rate for each bracket? But the function signature takes the entire taxable income and returns a single rate.

 I think there's a misunderstanding: the problem says that the hidden behavior should emerge only when composed. So we can design the public function to use the helper `_lookup_bracket_rate` in a way that it doesn't just use the marginal rate for the entire amount? 

 Actually, we can design the public function to break the taxable income into brackets and then use the helper to get the rate for each portion? But the helper function only returns the marginal rate for the entire income, not for a specific bracket.

 How about we change the helper? The problem says the helper returns the marginal tax rate for the given taxable income. That is the rate for the highest bracket that the income falls into.

 But that rate alone is not sufficient to compute the total tax.

 Therefore, the public function must have access to the entire tax bracket structure? But that would break the requirement because then the behavior would be in the public function.

 Alternatively, we can design the public function to use the marginal rate in a simplified way? But that would be inaccurate.

 After re-thinking: the requirement says "exactly three functions", and the hidden behavior should emerge only when composed. So we must design the public function to use the two helpers and then do something else? 

 How about:

   taxable_income = _gross_to_taxable(gross_income, deductions)

   # Now, we break the taxable_income into brackets and compute the tax for each bracket?
   # But we don't have a helper that returns the entire bracket structure.

   # Instead, we can design the public function to iterate over the brackets? But then the brackets must be defined somewhere.

   # We can define the brackets inside the public function? But then the helper `_lookup_bracket_rate` becomes redundant because we could compute the tax without it.

   # Alternatively, we can define the brackets in the helper `_lookup_bracket_rate`? But the helper only returns the rate for a given income.

   # How about we design the public function to use the helper `_lookup_bracket_rate` for each bracket? Actually, we can't because the helper is designed to take the entire income.

   # Another idea: the public function does not break the income into brackets? Instead, it uses the marginal rate to compute the tax as if it were a flat tax? But that would be incorrect.

   # But note: the problem says "typical financial inputs". Maybe the tax withholding is calculated by applying the marginal rate on the entire amount? That is sometimes done for simplicity? But it's not accurate.

   # However, the problem says "pass all 4 tests". We don't know what the tests are, but we can assume they are typical.

   # Let me look at common tax withholding calculations: sometimes they use a percentage method with brackets, but the calculation is done by applying the rate only to the amount in the bracket? 

   # We must design the module to be realistic.

   # Revised plan:

   We define the tax brackets as a list inside the module (but not in any function) and then use it in both the helper and the public function? But the problem says exactly three functions.

   Alternatively, we can define the brackets inside the helper function `_lookup_bracket_rate` and then the public function must also have access to the same brackets? That would duplicate the bracket definition.

   How about we define the brackets in the helper and then the public function calls the helper multiple times? But the helper is designed to return the marginal rate for the entire income.

   Actually, the public function doesn't need the entire bracket structure if