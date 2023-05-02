from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST
)


def test_paraphrase_list_api(client):
    url = reverse("paraphrase")

    # request without the required query parameter "tree"
    response = client.get(url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {'tree': ['This field may not be null.']}

    # request with invalid parse tree (e.g. plain text)
    text = "The charming Gothic Quarter, or Barri Gòtic, has narrow medieval " \
           "streets filled with trendy bars, clubs and Catalan restaurants"
    response = client.get(url + "?tree=" + text)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {'tree': ['Invalid parse tree']}

    # request with valid parse tree that has no variations
    tree = "(S (NP I) (VP (V enjoyed) (NP my cookie)))"
    response = client.get(url + "?tree=" + tree)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == \
           {"tree": ["Cannot generate any variation of the given parse tree"]}

    # request with valid parse tree
    tree = "(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) ) " \
           "(, ,) (CC or) (NP (NNP Barri) (NNP Gòtic) ) ) (, ,) (VP (VBZ has)" \
           " (NP (NP (JJ narrow) (JJ medieval) (NNS streets) ) (VP (VBN fille" \
           "d) (PP (IN with) (NP (NP (JJ trendy) (NNS bars) ) (, ,) (NP (NNS " \
           "clubs) ) (CC and) (NP (JJ Catalan) (NNS restaurants) ) ) ) ) ) ) )"
    response = client.get(url + "?tree=" + tree)
    assert response.status_code == HTTP_200_OK
    assert response.json()["paraphrases"]

    # request with invalid limit (not a positive integer)
    tree = "(S (NP I) (VP (V enjoyed) (NP my cookie)))"
    limit = "0"
    response = client.get(url + "?tree=" + tree + "&limit=" + limit)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == \
           {"limit": ["Limit must be a positive integer"]}

    # request with valid parse tree and valid limit
    tree = "(S (NP (NP (DT The) (JJ charming) (NNP Gothic) (NNP Quarter) ) " \
           "(, ,) (CC or) (NP (NNP Barri) (NNP Gòtic) ) ) (, ,) (VP (VBZ has)" \
           " (NP (NP (JJ narrow) (JJ medieval) (NNS streets) ) (VP (VBN fille" \
           "d) (PP (IN with) (NP (NP (JJ trendy) (NNS bars) ) (, ,) (NP (NNS " \
           "clubs) ) (CC and) (NP (JJ Catalan) (NNS restaurants) ) ) ) ) ) ) )"
    # a tree above has 5 variations (original tree doesn't count), so the limit
    #  below actually limits the number of variations in the response
    limit = 3
    response = client.get(url + "?tree=" + tree + "&limit=" + str(limit))
    assert response.status_code == HTTP_200_OK
    assert len(response.json()["paraphrases"]) == limit
