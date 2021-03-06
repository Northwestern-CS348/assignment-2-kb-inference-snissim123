import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []


    def kb_retractR(self, fact_or_rule):
        if type(fact_or_rule) == Fact:
            # not in KB
            if not self.facts.count(fact_or_rule):
                return
            else:
                myF = self._get_fact(fact_or_rule)
                if not myF.asserted:
                    if not myF.supported_by:
                        for child in myF.supports_rules:
                            for pair in child.supported_by:
                                if pair[0] == myF:
                                    child.supported_by.remove(pair)

                                if len(child.supported_by) == 0:
                                    self.kb_retractR(child)


                        for child in myF.supports_facts:
                            for pair in child.supported_by:
                                if pair[0] == myF:
                                    child.supported_by.remove(pair)
                                if len(child.supported_by) == 0:
                                    self.kb_retractR(child)
                    
                        self.facts.remove(myF)

        else:
            if not self.rules.count(fact_or_rule):
                return
            myR = self._get_rule(fact_or_rule)
            if not myR.asserted:
                if not myR.supported_by:
                    for child in myR.supports_rules:
                        for pair in child.supported_by:
                            if pair[1] == myR:
                                child.supported_by.remove(pair)
                            if len(child.supported_by) == 0:
                                self.kb_retractR(child)

                    for child in myR.supports_facts:
                        for pair in child.supported_by:
                            if pair[1] == myR:
                                child.supported_by.remove(pair)
                            if len(child.supported_by) == 0:
                                self.kb_retract(child)

                    self.rules.remove(myR)
        


    def kb_retract(self, fact_or_rule):
        if type(fact_or_rule) == Fact:
            myF = self._get_fact(fact_or_rule)
            if myF.asserted:
                myF.asserted = False
            self.kb_retractR(myF)


class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing 
        """           
        
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        possBindings = match(rule.lhs[0], fact.statement)
        supportList = [fact, rule]
        allBindings = []

        if possBindings:
            newInfo = instantiate(rule.rhs, possBindings)

            # New fact
            if len(rule.lhs) == 1:
                addMe = Fact(newInfo, [supportList])
                
            # New rule
            else:
                for i in range(len(rule.lhs) - 1):
                    moreBindings = instantiate(rule.lhs[1 + i], possBindings)
                    allBindings.append(moreBindings)

                addMe = Rule([allBindings, newInfo], [supportList])

            addMe.asserted = False
            rule.supports_facts.append(addMe)
            fact.supports_facts.append(addMe)
            kb.kb_assert(addMe)



