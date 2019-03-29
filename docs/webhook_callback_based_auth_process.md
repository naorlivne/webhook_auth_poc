Alice needs Bob to do something for her, being great friends it's a given he will agree to help but only if he can ensure that it's Alice asking his help rather then Eve (his crazy ex).

Both Alice & Bob trust the mail company & carriers (this represents trust in a good HTTPS system that ensures no MITM attacks), the problem is that while Alice knows she can send a letter to Bob without it being modified or read by a third party Bob home address is also known to Eve which could just as easily put her name in the return address of a letter and claim to be Alice inside the letter, what Bob needs is some sort of proof that Alice is really is the one who sent the letter, to make matters worse both Alice & Bob haven't got any sort of preshared secret they can rely on. 

To solve this problem of authentication Alice & Bob do the following process to confirm Alice identity:

1. Alice creates a random token, she then hashes said token and saves both the hashed & unhashed results of the token.
2. Alice sends Bob a letter with her return address and two notes inside, one is the hashed version of the token & another is the request of what she needs him to do.
3. Upon receiving the letter Bob compares the return address on the envelope to Alice real address (which he already knows), on it's own this doesn't prevent Eve from just writing Alice return address which is where the rest of the steps comes in.
4. Bob writes down the hashed version of the token (keeping a copy to himself) & then sends in a new envelope to Alice return address this hashed token and prepaid envelope reply to him (this is equivalent to receiving a reply to a request in HTTPS which do to HTTPS being MITM safe you know for sure who you contacted is who it is).
5. Upon receiving the letter with the hashed version of the token Alice checks the records of all the hashed token she sent to people and check that she first has this token and that it was Bob the one she sent this token to.
6. Alice then sends Bob the unhashed version of the token using his prepaid envelope.
7. Bob then checks that the unhashed version & the hashed version of the token matches & that it was returned in the prepaid envelope he sent out.
8. Bob do whatever it is Alice asked him to (he's really nice).
9. For every new request Alice repeats the process.

This of course assume that no man in the middle is possible which makes HTTPS so important in the authentication step but in affect it allows Alice & Bob to use their home addresses as the "something they have" to prove authentication by ownership of the home addresses.

The most obvious real world usage I can currently think of for this is to use as an authentication method of API-to-API communication, whereby each API also has a webhook & in affect uses it's DNS address as his proof of identity, requiring HTTPS makes it safe against MITM attacks.

A proof of concept of such a webhook callback based authentication process (WCBA for short) is available at https://github.com/naorlivne/webhook_auth_poc

Benefits of WCBA is that it doesn't requires storing any secrets long term as each token is a single use & that it requires no prior sharing of secrets such as passwords, this is similar to the way certification providers often require one to add a record to their DNS in order to prove ownership of the domain in that both use the domain ownership as the proof of identity.