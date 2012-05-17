#include <iostream>

using namespace std;

void simpleMethod()
{
	// Declare the variables that will hold the input given by the user
	string w0, w1, w2, w3, w4, w5, w6, w7, w8, w9;
	
	cout << "Enter enter 10 words than hit enter: ";

	cin >> w0 >> w1 >> w2 >> w3 >> w4 >> w5 >> w6 >> w7 >> w8 >> w9;

	cout << "There once was a girl named " << w0 << " and she had a big "
	     << w1 << ". She had a\n"
	     << "father named " << w2 << "..." << endl;
}

int main()
{
	simpleMethod();
	return 0;
}
