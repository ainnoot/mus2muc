%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Search %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#const k=0.
{ last_state(T): T=0..k-1 } = 1.
time(0..T) :- last_state(T).
{ trace(T,X): atomic(_,X) } :- time(T).
:- root(X), not holds(0, X).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Atomic Formula %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(T, X) :- atomic(X, A), time(T), trace(T, A).
holds(T, X) :- last(X), last_state(T).
holds(T, X) :- true(X), time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%% Propositional Formula %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(T, X) :- conjunction(X,_), time(T), holds(T,F): conjunction(X,F).
holds(T, X) :- disjunction(X, F), holds(T, F).
holds(T, X) :- negate(X, F), not holds(T, F), time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Temporal Formula %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(T, X) :- next(X, F), holds(T+1, F), time(T), time(T+1).
holds(T, X) :- until(X, LHS, RHS), holds(T, RHS).
holds(T, X) :- until(X, LHS, RHS), holds(T, LHS), holds(T+1, X).
holds(T, X) :- release(X, LHS, RHS), holds(T,RHS), holds(T,LHS).
holds(T, X) :- release(X, LHS, RHS), holds(T,RHS), holds(T+1, X).
holds(T, X) :- release(X, LHS, RHS), holds(T,RHS), last_state(T).

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Syntactic sugar %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% holds(T, X) :- weak_next(X, F), holds(T+1,F), time(T), time(T+1).
% holds(T, X) :- weak_next(X, F), last_state(T).
% holds(T, X) :- eventually(X, F), holds(T, F).
% holds(T, X) :- eventually(X, F), holds(T+1, X), time(T+1).
% holds(T, X) :- always(X, F), holds(T, F), holds(T+1, X).
% holds(T, X) :- always(X, F), holds(T, F), last_state(T).
% holds(T, X) :- equals(X, LHS, RHS), holds(T, LHS), holds(T, RHS).
% holds(T, X) :- equals(X, LHS, RHS), time(T), not holds(T, LHS), not holds(T, RHS).
% holds(T, X) :- implies(X, LHS, _), time(T), not holds(T, LHS).
% holds(T, X) :- implies(X, _, RHS), holds(T, RHS).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Output projection %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#show __mus__/1.
