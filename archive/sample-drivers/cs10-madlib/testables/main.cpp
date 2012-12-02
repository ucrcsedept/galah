#include <iostream>
#include <vector>
#include <cctype>

using namespace std;

/// A very unimaginitive lorem ipsum generator
class LoremIpsumGenerator {
    // The chunk of lorem ipsum the generator will pull from
    static const string _LOREM_IPSUM;

	/// A counter holding where in the lorem ipsum chuck we are
	int _where;
	
public:
	LoremIpsumGenerator() : _where(0) {
		/* nothing to be done */
	}

	/// Gets a single word of lorem ipsum.
	string get_word() {
		// Advance the counter until we're at the beginning of a word
		for ( ; !isalpha(_LOREM_IPSUM[_where]); _where = (_where + 1) % _LOREM_IPSUM.size()) ;
		
		// Remember the starting position of the word
		int start = _where;
		
		// Find the end of the word
		for ( ; _LOREM_IPSUM[_where] != ' ' && _where < _LOREM_IPSUM.size(); ++_where) ;
		
		return _LOREM_IPSUM.substr(start, _where - start);
	}

	/// Will return a chunk of lorem ipsum at most ncharacters long.
    string get_until(size_t zncharacters) {
		string chunk;
		
		while (true) {
			int old_where = _where;
			string word = get_word();
			
			if (word.size() + chunk.size() + 1 <= zncharacters) {
				chunk += word + " ";
			} else {
				_where = old_where;
				break;
			}
		}
		
		// Cut off the trailing space
		if (chunk.size() != 0)
			chunk.resize(chunk.size() - 1);
		
		return chunk;
	}
};

const string LoremIpsumGenerator::_LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor. Pellentesque auctor nisi id magna consequat sagittis. Curabitur dapibus enim sit amet elit pharetra tincidunt feugiat nisl imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros. Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.";

string input(istream & zin = cin) {
	string buffer;
	zin >> buffer;
	return buffer;
}

int main()
{
	const int MAX_LINE_LENGTH = 80;
	const int NINPUTS = 10;
	const int NPARAGRAPHS = 3;
	const int NLINES_IN_PARAGRAPH = 5;
	
    LoremIpsumGenerator generator;
    
    vector<string> inputs;
    for (int i = 0; i < NINPUTS; ++i)
		inputs.push_back(input());
    
    int cur_input = 0;
    
    for (int i = 0; i < NPARAGRAPHS; ++i) {
		for (int i = 0; i < NLINES_IN_PARAGRAPH; ++i) {			
			if (cur_input >= inputs.size()) {
				cout << generator.get_until(MAX_LINE_LENGTH) << '\n';
			} else {
				string filler = generator.get_until(
					MAX_LINE_LENGTH - inputs[cur_input].size() - 1
				);
				
				cout << filler + " " + inputs[cur_input] << '\n';
				
				++cur_input;
			}
		}
		
		cout << '\n';
	}
    
    return 0;
}
