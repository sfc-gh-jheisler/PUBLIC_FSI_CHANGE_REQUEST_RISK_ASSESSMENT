# **Change Request Risk Assessment with Cortex AI**
### Author: **John Heisler** - Senior AI Specialist, Financial Services, Snowflake
In this notebook, we're going to evaluate a new change request and determine a risk score for that change request resulting in target environment instability.

The notebook is written to allow deployment directly into anyone's environment.

## Cortex AI Commercial Value

Ultimately, AI should drive commercial value. To that end, building, deploying, and maintaining the systems that underpin that commercial value need to be easy, efficient, and trusted. 

With Cortex AI, we balance complexity encapsulation with complexity exposure to maximize the time to value with AI. 

### Hit the Nail, Don't Build the Hammer!
Enterprises that maximize efforts leveraging their differentiated domain knowledge and creativity will ultimately win the AI race. Every ounce of effort spent on managing/building/tuning AI is a distraction from delivering value and thus comes at a material opportunity cost. With Snowflake Cortex AI, we aim to maximize efforts wielding the power of AI, not building it.

## Use Case Commercial Value
Our solution drives **operational alpha** by maximizing uptime of production environments. This solution provides operational alpha in at least these four ways:
1. **System Uptime**: The systems critical to support our portfolio teams will be more stable and provide maximum value to our portfolio teams' performance.
2. **Regulatory Reporting**: Minimize need for reporting to external regulators about critical system downtime and its impact.
3. **Opportunity Cost**: Minimizing time spent conducting emergency maintenance which can be repurposed to focus on alpha-generating solutions.
4. **Opportunity Cost**: Minimize need for time-and-resource-intensive root cause analysis and these cross functional teams can focus on their primary responsibilities.

## Process Outline
First, we will create and fill a change request table with some synthetic data (Fun Fact: You can use LLMs to do that. Check out how I did it in harbinger_data_creation.ipynb notebook in this repo). 

Second, we will build a python function to house our prompt and accept a change request as context. this approach streamlines our code and decouples the prompt from our broader development, allowing for independent development on the prompt by domain experts.

Last, we will build a Streamlit in Snowflake (SiS) front end to allow our end users to score new change requests.

## Snowflake Differentiators
* **LLM fungibility**: We have a model garden right here in Snowflake-- no need to manage divergent infrastructure and no need for external calls which introduce risk into your system
* **Physics of data**: With snowflake, we can perform the inference with LLMs all in one spot. There is no need to dehydrate Snowflake and move externally 
* **Flexibility**: Snowpark Container Services would allow you to bring any model you want (or any functionality for that matter) to run right here in Snowflake. This opens the door to run anything in Snowflake to maximize performance, minimize overhead, and reap the benefits of a single governance framework.
* **Access to Power**: We provide access to GPUs and infrastructure at your fingertips to turbo charge your development and performance. Again, this allows you to focus on driving value not button booping and knob twisting. 

## Art of the Possible
Here is some food for thought and hopefully inspiring enhancements for your deployment. 

* **Fine Tuning**: If we have tied incidents' root causes to change requests in the past, we could fine tune a model here in Snowflake with that data and the task that we're after. This has a couple of very interesting advantages. first, we would have a very specialize model that may perform this task very well because it has "experience" with what good and bad looks like. More operationally focused, we could maybe use a smaller model maximizing cost efficiencies.
* **More Context - Metadata**: we could offer much more context about what each column in the data set means and fully define the json structure that we're passing. This would inform the model on the meaning of each column rather than allowing it to come up with its best guess at the columns.
* **More Context - Target System Stability (Windshield)**: We could use another LLM upstream of the final risk inference to build a synopsis of the target system stability and status. For instance, it could state things like, "the target system for EDM-Account-Master has seen several out of memory alerts and disc space errors in the last six weeks." We would instruct the risk prompt to consider that environment when deriving its risk assessment which should enhance its predictions.
* **More Context - Incident Root Causes (Rear view Mirror)**: We could pass a synopsis of the last 6 months of root causes to the model. This would make it keenly aware 

## Next Steps
1. Try this out on your own data: You will be *blown away* by the results and how easy it is. 
2. Don't walk alone: You have access to AI experts that can guide your development to an accelerated outcome at no cost to you!
