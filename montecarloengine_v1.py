
import random

class SalesAssumptions:
    def __init__(self):
        self.calls_per_day = 20 
        self.meeting_rate = 0.25
        self.close_rate = 0.25
        self.avg_deal_size = 4000
        self.sales_cycle_days = 30
        self.recurring_probability = .03
        self.commission_rate = 0.50
    
class SalesSimulator:
    def __init__(self, assumptions):
        self.assumptions = assumptions
        self.day = 0
        self.pending_deals = []
    

    def reset(self):
        """ Reset simulator state so a new simulation run starts from day 0."""
        self.day = 0
        self.pending_deals = []

    def simulate_day(self):
        """
        Simulates one day of sales activity + any deals that close today.

        Returns a dictionary with today's metrics

        """
        a = self.assumptions # local alias (so I don't have to keep typing self.assumption)

        # --------------------
        # 1) Process deals that close today 
        # --------------------
        closed_today = []
        still_pending = []

        for deal in self.pending_deals:
            close_day, commission_amount, is_recurring = deal # tuple unpacking, review tuples later
            if close_day == self.day:
                closed_today.append(deal) #need to revisit .append
            else:
                still_pending.append(deal)

        #Update pending deals list to remove the ones that closed today
        self.pending_deals = still_pending

        commission_earned_today = 0.0
        recurring_deals_closed_today = 0

        for close_day, commission_amount, is_recurring in closed_today:
            commission_earned_today += commission_amount
            if is_recurring:
                recurring_deals_closed_today += 1

        deals_closed_today = len(closed_today)

        #-----------------
        #2) Simulate today's outbound activity 
        #-----------------
        meetings_set_today = 0 
        deals_created_today = 0 

        for _ in range(a.calls_per_day):
            #Does this call turn into a meeting?
            if random.random() < a.meeting_rate:
                meetings_set_today += 1
        
        # For each meeting, does it turn into a deal?
        for _ in range(meetings_set_today):
            if random.random() < a.close_rate:
                deals_created_today += 1 

                # Commission amount for this deal
                commission_amount = a.avg_deal_size * a.commission_rate

                # Will it become recurring or not?
                is_recurring = random.random() < a.recurring_probability

                # When does it close? 
                close_day = self.day + a.sales_cycle_days

                # Add to pending deals queue
                self.pending_deals.append((close_day, commission_amount, is_recurring))

        # --------------------
        # 3) Wrap up the day and return metrics.
        #----------------------

        summary = {
            "day": self.day, 
            "calls": a.calls_per_day,
            "meetings_set": meetings_set_today,
            "deals_created": deals_created_today,
            "deals_closed": deals_closed_today,
            "recurring_deals_closed": recurring_deals_closed_today,
            "commission_earned": commission_earned_today, 
            "pending_deals": len(self.pending_deals), 

        }

        self.day += 1 #move to the next day 
        return summary
    

    def simulate_month(self):
        pass

    def run_simulation(self, months=4, iterations=100):
        """ 
        Allows me to run many iterations over the course of months (Monte Carlo).
    
        months: number of months to simulate (30 day assumption)

        iterations: how many simulated futures to run

        Return: list of total commission earned in each simulation run"""

        days = months * 30 # approximate days per month for easieness
        totals = []        # list to store total commission per run 

        for _ in range(iterations):
            # Reset state at the start of each independent run 
            self.reset()

            total_commission = 0.0

            for _ in range(days):
                day_summary = self.simulate_day()
                total_commission += day_summary["commission_earned"]
            
            totals.append(total_commission)

        return totals
    
    def summarize_results(self):
        pass

if __name__ == "__main__":
    assumptions = SalesAssumptions()
    simulator = SalesSimulator(assumptions)

    totals = simulator.run_simulation(months=4, iterations=1000)

    print("Ran", len(totals), "simulations")
    print("Example totals (first 10):", totals[:10])

    #simulator.run_simulation() 
    #simulator.summarize_results()

#this is just to see how reset() is being used
    """ print("Before reset:", simulator.day, len(simulator.pending_deals))
    simulator.simulate_day()
    simulator.simulate_day()
    print("After 2 days:", simulator.day, len(simulator.pending_deals))

    simulator.reset()
    print("After reset:", simulator.day, len(simulator.pending_deals)) """
    
    #for _ in range(120):
        #print(simulator.simulate_day())

